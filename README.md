# Local KP Astrology AI

A local-first KP Astrology web application scaffold with real Swiss Ephemeris calculations, Placidus cusps, KP ayanamsa, Vimshottari sub/sub-sub lords, deterministic significator rules, prediction JSON, and optional local LLM interpretation through Ollama or LM Studio.

## Features

- **No external astrology APIs**: calculations are performed in the Python backend with `pyswisseph`.
- **KP core**: KP ayanamsa, Placidus cusps, nakshatra, star lord, sub lord, sub-sub lord, Rahu/Ketu, and retrograde detection.
- **Significators**: four deterministic levels for every planet and a planet-vs-house matrix.
- **Dasha**: Vimshottari Mahadasha through Sookshma-style nested periods from the KP-corrected Moon longitude.
- **Ruling Planets**: real-time ascendant sign/star lord, Moon sign/star lord, and weekday lord.
- **Prediction modules**: marriage, career, health, property, foreign travel/settlement, children, education, wealth, longevity, and horary rule shells.
- **Local AI**: Ollama (`http://localhost:11434`) and LM Studio (`http://localhost:1234/v1`) adapters with an LLM-as-judge validation pass.
- **Storage**: SQLite tables for saved charts, user queries, and golden charts.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Local LLM

Install Ollama and pull a model locally:

```bash
ollama pull llama3
```

If Ollama/LM Studio is not running, the API returns the deterministic structured KP JSON with a warning instead of sending data to a cloud service.

## Docker

```bash
docker compose up --build
```

Then open the frontend at `http://localhost:5173` and the API at `http://localhost:8000/docs`.

## One-file mobile version

If you want the whole usable app in one Python file, run `mobile_kp_app.py`. It serves a mobile-friendly HTML interface and the KP calculation API from the same file.

```bash
pip install fastapi uvicorn pyswisseph httpx pydantic
uvicorn mobile_kp_app:app --host 0.0.0.0 --port 8000
```

Use it on:

- The same computer: `http://localhost:8000`
- A mobile phone on the same Wi-Fi: `http://<your-computer-LAN-IP>:8000`

To find your LAN IP:

```bash
hostname -I
```

Keep Ollama running on the computer if you want the local AI explanation:

```bash
ollama serve
ollama pull llama3
```

The phone is only a browser. All astrology calculations and local AI calls still run on your own computer; no cloud astrology API is used.
