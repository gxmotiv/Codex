from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .engine import compute_chart
from .interpretation import interpret_chart

HTML = """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Jyotish Offline Web App</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }
    .card { background: #111827; border: 1px solid #374151; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 0.75rem; }
    input, select, button, textarea { width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid #475569; background: #1f2937; color: #e2e8f0; }
    button { cursor: pointer; background: #2563eb; border: none; font-weight: 600; }
    pre { white-space: pre-wrap; background: #020617; padding: 1rem; border-radius: 8px; overflow-x: auto; }
    .muted { color: #94a3b8; font-size: 0.9rem; }
  </style>
</head>
<body>
  <h1>Jyotish Offline Web App</h1>
  <p class='muted'>Engine #1 + System #1 in-browser form. No external API usage.</p>

  <div class='card'>
    <h2>Chart Input</h2>
    <div class='grid'>
      <label>Request ID<input id='request_id' value='demo-web-1'></label>
      <label>Date/Time (local)<input id='datetime_local' value='1992-10-14T08:45:00'></label>
      <label>Timezone<input id='timezone' value='Asia/Kolkata'></label>
      <label>Latitude<input id='latitude' type='number' step='any' value='28.6139'></label>
      <label>Longitude<input id='longitude' type='number' step='any' value='77.2090'></label>
      <label>Ayanamsha (deg)<input id='ayanamsha_deg' type='number' step='any' value='24.0'></label>
      <label>Node Mode
        <select id='node_mode'>
          <option value='true'>true</option>
          <option value='mean'>mean</option>
        </select>
      </label>
    </div>
    <br>
    <button id='runBtn'>Run Interpretation</button>
  </div>

  <div class='card'>
    <h2>Output</h2>
    <pre id='output'>{"status":"ready"}</pre>
  </div>

<script>
document.getElementById('runBtn').addEventListener('click', async () => {
  const payload = {
    request_id: document.getElementById('request_id').value,
    datetime_local: document.getElementById('datetime_local').value,
    timezone: document.getElementById('timezone').value,
    latitude: Number(document.getElementById('latitude').value),
    longitude: Number(document.getElementById('longitude').value),
    config: {
      ayanamsha_deg: Number(document.getElementById('ayanamsha_deg').value),
      house_system: 'whole_sign',
      node_mode: document.getElementById('node_mode').value
    }
  };

  const out = document.getElementById('output');
  out.textContent = 'Running...';
  try {
    const res = await fetch('/api/interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = JSON.stringify({error: String(e)}, null, 2);
  }
});
</script>
</body>
</html>
"""


def build_result(payload: dict[str, Any]) -> dict[str, Any]:
    chart = compute_chart(payload)
    interpretation = interpret_chart(chart)
    return {"chart": chart, "interpretation": interpretation}


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self.send_error(404, "Not Found")
            return
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/interpret":
            self.send_error(404, "Not Found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            result = build_result(payload)
        except Exception as exc:  # broad for robust api errors
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, result)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Jyotish web app running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
