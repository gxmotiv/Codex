"""Single-file mobile KP Astrology web app.

Run:
    pip install fastapi uvicorn pyswisseph httpx pydantic
    uvicorn mobile_kp_app:app --host 0.0.0.0 --port 8000

Open on the same computer: http://localhost:8000
Open on a phone on the same Wi-Fi: http://<your-computer-lan-ip>:8000
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx
import swisseph as swe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
OUTER_PLANETS = ["Uranus", "Neptune", "Pluto"]
VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}
NAKSHATRA_NAMES = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
NAKSHATRA_SPAN = 360.0 / 27.0
SWISS_PLANETS = {"Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4, "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9, "Rahu": 11}
MODULE_RULES = {
    "marriage": {"primary": [2, 7, 11], "obstacles": [1, 6, 10, 12, 4], "cusp": 7},
    "career": {"primary": [6, 2, 10, 11], "obstacles": [8, 12], "cusp": 10},
    "health": {"primary": [5, 11], "obstacles": [6, 8, 12], "cusp": 1},
    "property": {"primary": [4, 11, 12], "obstacles": [8], "cusp": 4},
    "foreign": {"primary": [3, 9, 12], "obstacles": [4, 8], "cusp": 12},
    "children": {"primary": [2, 5, 11], "obstacles": [1, 4, 10, 12], "cusp": 5},
    "education": {"primary": [4, 9, 11], "obstacles": [8], "cusp": 4},
    "wealth": {"primary": [2, 6, 10, 11], "obstacles": [8, 12], "cusp": 2},
    "horary": {"primary": [1, 11], "obstacles": [8, 12], "cusp": 1},
}
RULE_LIBRARY = [
    "Marriage: 7th cusp sub-lord must signify 2, 7, 11; 1, 6, 10, 12 obstruct.",
    "Career/job: judge 6, 2, 10, 11. Business adds 7 and 5.",
    "Foreign: judge 3, 9, 12; 4 anchors to motherland; 8 shows visa crisis.",
    "Wealth: judge 2, 6, 10, 11; loss through 8 and 12.",
]


def norm(deg: float) -> float:
    return deg % 360.0


def sign_name(lon: float) -> str:
    return SIGN_NAMES[int(norm(lon) // 30)]


def dms(lon: float) -> str:
    lon = norm(lon)
    within = lon % 30
    deg = int(within)
    minutes_float = (within - deg) * 60
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        deg += 1
    return f"{sign_name(lon)} {deg:02d}°{minutes:02d}'{seconds:02d}\""


def ordered_from(lord: str) -> list[str]:
    idx = VIMSHOTTARI_ORDER.index(lord)
    return VIMSHOTTARI_ORDER[idx:] + VIMSHOTTARI_ORDER[:idx]


def sub_lord_at(offset_deg: float, parent_span: float, start_lord: str) -> tuple[str, float, float]:
    cursor = 0.0
    for lord in ordered_from(start_lord):
        span = parent_span * VIMSHOTTARI_YEARS[lord] / 120.0
        if offset_deg <= cursor + span + 1e-10:
            return lord, cursor, span
        cursor += span
    return ordered_from(start_lord)[-1], cursor, parent_span - cursor


def division_info(lon: float) -> dict[str, Any]:
    lon = norm(lon)
    nak_index = min(26, int(lon // NAKSHATRA_SPAN))
    nak_start = nak_index * NAKSHATRA_SPAN
    offset = lon - nak_start
    star_lord = VIMSHOTTARI_ORDER[nak_index % 9]
    sub_lord, sub_start, sub_span = sub_lord_at(offset, NAKSHATRA_SPAN, star_lord)
    sub_sub_lord, _, _ = sub_lord_at(offset - sub_start, sub_span, sub_lord)
    sign = sign_name(lon)
    return {"longitude": lon, "dms": dms(lon), "sign": sign, "sign_lord": SIGN_LORDS[sign], "nakshatra": NAKSHATRA_NAMES[nak_index], "star_lord": star_lord, "sub_lord": sub_lord, "sub_sub_lord": sub_sub_lord, "nakshatra_index": nak_index}


def local_dt(date: str, time: str, tz: str) -> datetime:
    return datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=ZoneInfo(tz))


def julian_day(dt: datetime) -> float:
    utc = dt.astimezone(timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    return swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)


def set_kp_mode() -> None:
    sidm_kp = getattr(swe, "SIDM_KRISHNAMURTI", getattr(swe, "SIDM_KRISHNAMURTI_VP291", swe.SIDM_LAHIRI))
    swe.set_sid_mode(sidm_kp, 0, 0)


def between(start: float, end: float, point: float) -> bool:
    start, end, point = norm(start), norm(end), norm(point)
    return start <= point < end if start <= end else point >= start or point < end


def house_for(lon: float, cusps: dict[int, dict[str, Any]]) -> int:
    values = [cusps[i]["longitude"] for i in range(1, 13)]
    for idx in range(12):
        if between(values[idx], values[(idx + 1) % 12], lon):
            return idx + 1
    return 12


def calc_cusps(dt: datetime, lat: float, lon: float) -> dict[int, dict[str, Any]]:
    set_kp_mode()
    values, _ = swe.houses_ex(julian_day(dt), lat, lon, b"P", swe.FLG_SIDEREAL)
    cusps = {}
    for house in range(1, 13):
        info = division_info(values[house - 1])
        cusps[house] = {"house": house, "longitude": info["longitude"], "longitude_dms": info["dms"], **{k: info[k] for k in ["sign", "sign_lord", "nakshatra", "star_lord", "sub_lord", "sub_sub_lord"]}}
    return cusps


def calc_planets(dt: datetime, lat: float, lon: float, topocentric: bool) -> dict[str, dict[str, Any]]:
    set_kp_mode()
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    if topocentric:
        swe.set_topo(lon, lat, 0)
        flags |= swe.FLG_TOPOCTR
    jd = julian_day(dt)
    out: dict[str, dict[str, Any]] = {}
    rahu_lon = 0.0
    for name in PLANETS + OUTER_PLANETS:
        if name == "Ketu":
            plon, plat, speed = norm(rahu_lon + 180), 0.0, 0.0
        else:
            values, _ = swe.calc_ut(jd, SWISS_PLANETS[name], flags)
            plon, plat, _dist, speed, *_ = values
            if name == "Rahu":
                rahu_lon = plon
        info = division_info(plon)
        out[name] = {"name": name, "longitude": info["longitude"], "longitude_dms": info["dms"], "latitude": plat, "speed": speed, "retrograde": speed < 0, **{k: info[k] for k in ["sign_lord", "nakshatra", "star_lord", "sub_lord", "sub_sub_lord"]}}
    return out


def houses_owned(planet: str, cusps: dict[int, dict[str, Any]]) -> list[int]:
    return [h for h, c in cusps.items() if SIGN_LORDS[sign_name(c["longitude"])] == planet]


def significators(planets: dict[str, dict[str, Any]], cusps: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    occupied = {name: house_for(data["longitude"], cusps) for name, data in planets.items()}
    out = {}
    for planet, data in planets.items():
        star = data["star_lord"]
        l1 = [occupied[star]] if star in occupied else []
        l2 = [occupied[planet]]
        l3 = houses_owned(star, cusps)
        l4 = houses_owned(planet, cusps)
        out[planet] = {"star_lord": star, "levels": {"1_star": l1, "2_occupation": l2, "3_star_lord_ownership": l3, "4_planet_ownership": l4}, "strong_houses": sorted(set(l1 + l2)), "weak_houses": sorted(set(l3 + l4)), "all_houses": sorted(set(l1 + l2 + l3 + l4))}
    return out


def dasha_tree(moon_lon: float, birth_dt: datetime, depth: int = 3) -> list[dict[str, Any]]:
    def periods(start: datetime, lord_order: list[str], total_years: float, child_depth: int) -> list[dict[str, Any]]:
        rows, cursor = [], start
        for lord in lord_order:
            years = total_years * VIMSHOTTARI_YEARS[lord] / 120.0
            end = cursor + timedelta(days=years * 365.2425)
            row = {"lord": lord, "start": cursor.isoformat(), "end": end.isoformat()}
            if child_depth > 1:
                row["children"] = periods(cursor, ordered_from(lord), years, child_depth - 1)
            rows.append(row)
            cursor = end
        return rows

    info = division_info(moon_lon)
    elapsed = moon_lon - info["nakshatra_index"] * NAKSHATRA_SPAN
    first_lord = info["star_lord"]
    first_years = VIMSHOTTARI_YEARS[first_lord] * ((NAKSHATRA_SPAN - elapsed) / NAKSHATRA_SPAN)
    first_end = birth_dt + timedelta(days=first_years * 365.2425)
    rows = [{"lord": first_lord, "start": birth_dt.isoformat(), "end": first_end.isoformat(), "children": periods(birth_dt, ordered_from(first_lord), first_years, depth - 1)}]
    cursor = first_end
    for lord in ordered_from(first_lord)[1:] + ordered_from(first_lord)[:1]:
        end = cursor + timedelta(days=VIMSHOTTARI_YEARS[lord] * 365.2425)
        rows.append({"lord": lord, "start": cursor.isoformat(), "end": end.isoformat(), "children": periods(cursor, ordered_from(lord), VIMSHOTTARI_YEARS[lord], depth - 1)})
        cursor = end
    return rows


def current_dasha(tree: list[dict[str, Any]], at: datetime) -> list[str]:
    result, rows = [], tree
    while rows:
        found = next((r for r in rows if datetime.fromisoformat(r["start"]) <= at < datetime.fromisoformat(r["end"])), None)
        if not found:
            break
        result.append(found["lord"])
        rows = found.get("children", [])
    return result


class ChartRequest(BaseModel):
    name: str = "Native"
    date: str = Field(default="1990-05-15")
    time: str = Field(default="10:30:00")
    timezone: str = "Asia/Kolkata"
    latitude: float = 19.076
    longitude: float = 72.8777
    topocentric: bool = True


class PredictRequest(BaseModel):
    chart: ChartRequest
    module: str = "marriage"
    question: str = "When will I get married?"
    use_llm: bool = True
    model: str = "llama3"


def build_chart(req: ChartRequest, at: datetime | None = None) -> dict[str, Any]:
    birth = local_dt(req.date, req.time, req.timezone)
    cusps = calc_cusps(birth, req.latitude, req.longitude)
    planets = calc_planets(birth, req.latitude, req.longitude, req.topocentric)
    for planet in planets.values():
        planet["house"] = house_for(planet["longitude"], cusps)
    sigs = significators(planets, cusps)
    tree = dasha_tree(planets["Moon"]["longitude"], birth)
    now = at or datetime.now(tz=birth.tzinfo)
    current_cusps = calc_cusps(now, req.latitude, req.longitude)
    current_planets = calc_planets(now, req.latitude, req.longitude, True)
    rp = [current_cusps[1]["sign_lord"], current_cusps[1]["star_lord"], current_planets["Moon"]["sign_lord"], current_planets["Moon"]["star_lord"], WEEKDAY_LORDS[now.weekday()]]
    return {"input": req.model_dump(), "kp_ayanamsa": float(swe.get_ayanamsa_ut(julian_day(birth))), "planets": planets, "cusps": cusps, "significators": sigs, "current_dasha": current_dasha(tree, now), "ruling_planets": list(dict.fromkeys(rp)), "dasha_tree": tree}


def evaluate(module: str, chart: dict[str, Any], question: str) -> dict[str, Any]:
    if module not in MODULE_RULES:
        module = "marriage"
    rules = MODULE_RULES[module]
    cusp = chart["cusps"][rules["cusp"]]
    sub = cusp["sub_lord"]
    sub_sig = chart["significators"].get(sub, {})
    all_houses = set(sub_sig.get("all_houses", []))
    primary = set(rules["primary"])
    obstacles = set(rules["obstacles"])
    primary_hits = sorted(all_houses & primary)
    obstacle_hits = sorted(all_houses & obstacles)
    score = min(100, max(0, 35 + 15 * len(primary_hits) - 8 * len(obstacle_hits)))
    return {"module": module, "question": question, "queried_cusp": rules["cusp"], "queried_cusp_sub_lord": sub, "sub_lord_significations": sub_sig, "primary_houses": sorted(primary), "obstacle_houses": sorted(obstacles), "primary_hits": primary_hits, "obstacle_hits": obstacle_hits, "current_dasha": chart["current_dasha"], "ruling_planets": chart["ruling_planets"], "confidence_score": score, "verdict": "supportive" if len(primary_hits) >= 2 else "mixed" if primary_hits else "weak_or_denied", "kp_rules": RULE_LIBRARY}


async def local_llm(structured: dict[str, Any], model: str) -> dict[str, Any]:
    prompt = "You are a senior KP Astrologer. Use only this JSON; do not hallucinate planets or houses. Explain the result simply for a mobile user.\n" + str(structured)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False, "temperature": 0.2})
            response.raise_for_status()
            return {"available": True, "text": response.json().get("response", "")}
    except Exception as exc:
        return {"available": False, "warning": f"Ollama is not reachable on this machine: {exc}", "text": None}


HTML = r"""
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Mobile KP Astrology AI</title><style>
*{box-sizing:border-box}body{margin:0;background:#070b15;color:#e5e7eb;font-family:system-ui,-apple-system,Segoe UI,sans-serif}header{position:sticky;top:0;z-index:2;background:#0f172acc;border-bottom:1px solid #263149;backdrop-filter:blur(12px);padding:14px 16px}h1{font-size:20px;margin:0}p{color:#aeb8cb}.wrap{display:grid;gap:14px;padding:14px;max-width:1040px;margin:auto}.card{background:linear-gradient(180deg,#151b2e,#0d1324);border:1px solid #263149;border-radius:18px;padding:14px;box-shadow:0 20px 50px #0008}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}label{font-size:12px;color:#aeb8cb}input,select,textarea,button{width:100%;border-radius:12px;border:1px solid #334155;background:#080d19;color:#fff;padding:11px;font:inherit}button{background:#7c3aed;border:0;font-weight:800;margin-top:10px}.wheel{width:100%;max-width:360px;display:block;margin:auto}.ring{fill:#101827;stroke:#4f46e5}.cusp{stroke:#f59e0b;stroke-width:1.3}.nak{stroke:#334155;stroke-width:.5}.planet{fill:#38bdf8}.rx{fill:#fb923c}.glyph{font-size:8px;font-weight:800;fill:#06111f}table{width:100%;border-collapse:collapse;font-size:12px}td,th{padding:8px;border-bottom:1px solid #263149;text-align:left}pre{white-space:pre-wrap;overflow:auto;max-height:360px;background:#050816;border:1px solid #263149;border-radius:12px;padding:10px;color:#c4b5fd}.pill{display:inline-block;background:#172554;color:#bfdbfe;border:1px solid #3b82f6;border-radius:999px;padding:4px 9px;margin:3px}@media(max-width:720px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}h1{font-size:18px}.card{border-radius:14px;padding:12px}.wrap{padding:10px}table{font-size:11px}}
</style></head><body><header><h1>📱 Mobile KP Astrology AI</h1><p style="margin:4px 0 0">One-file local app. Calculations stay on your computer.</p></header><main class="wrap">
<section class="card"><h2>Birth Data</h2><div class="grid"><label>Name<input id="name" value="Test Native"></label><label>Date<input id="date" type="date" value="1990-05-15"></label><label>Time<input id="time" type="time" step="1" value="10:30:00"></label><label>Timezone<input id="timezone" value="Asia/Kolkata"></label><label>Latitude<input id="latitude" type="number" step="0.0001" value="19.076"></label><label>Longitude<input id="longitude" type="number" step="0.0001" value="72.8777"></label><label>Mode<select id="topocentric"><option value="true">Topocentric</option><option value="false">Geocentric</option></select></label><label>Module<select id="module"><option>marriage</option><option>career</option><option>health</option><option>property</option><option>foreign</option><option>children</option><option>education</option><option>wealth</option><option>horary</option></select></label></div><label>Question<textarea id="question">When will I get married?</textarea></label><button onclick="calculate()">Calculate Chart</button><button onclick="predict()">Ask Local AI / Rules</button></section>
<section class="card"><h2>Wheel</h2><div id="wheel"></div><div id="summary"></div></section>
<section class="card"><h2>Prediction</h2><div id="prediction">Run prediction to see structured KP result.</div></section>
<section class="card"><h2>Planets</h2><div id="planets"></div></section><section class="card"><h2>Cusps</h2><div id="cusps"></div></section><section class="card"><h2>JSON</h2><pre id="json"></pre></section>
</main><script>
let chart=null;function val(id){return document.getElementById(id).value}function payload(){return{name:val('name'),date:val('date'),time:val('time'),timezone:val('timezone'),latitude:Number(val('latitude')),longitude:Number(val('longitude')),topocentric:val('topocentric')==='true'}}
function table(rows,heads,fn){return `<table><thead><tr>${heads.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${Object.values(rows).map(fn).join('')}</tbody></table>`}
function drawWheel(c){const pts=Object.values(c.planets).map(p=>{let a=(p.longitude-90)*Math.PI/180;return{...p,x:150+92*Math.cos(a),y:150+92*Math.sin(a)}});const cusps=Object.values(c.cusps).map(q=>{let a=(q.longitude-90)*Math.PI/180;return{...q,x1:150+65*Math.cos(a),y1:150+65*Math.sin(a),x2:150+134*Math.cos(a),y2:150+134*Math.sin(a)}});document.getElementById('wheel').innerHTML=`<svg viewBox="0 0 300 300" class="wheel"><circle cx="150" cy="150" r="140" class="ring"/><circle cx="150" cy="150" r="72" class="ring"/>${Array.from({length:27},(_,i)=>{let a=(i*13.333333-90)*Math.PI/180;return `<line x1="${150+116*Math.cos(a)}" y1="${150+116*Math.sin(a)}" x2="${150+140*Math.cos(a)}" y2="${150+140*Math.sin(a)}" class="nak"/>`}).join('')}${cusps.map(q=>`<line x1="${q.x1}" y1="${q.y1}" x2="${q.x2}" y2="${q.y2}" class="cusp"><title>Cusp ${q.house}: ${q.longitude_dms} ${q.sign_lord}/${q.star_lord}/${q.sub_lord}</title></line>`).join('')}${pts.map(p=>`<g><circle cx="${p.x}" cy="${p.y}" r="9" class="planet ${p.retrograde?'rx':''}"><title>${p.name} ${p.longitude_dms} H${p.house}</title></circle><text x="${p.x}" y="${p.y+3}" text-anchor="middle" class="glyph">${p.name[0]}${p.retrograde?'℞':''}</text></g>`).join('')}</svg>`}
function render(c){chart=c;drawWheel(c);document.getElementById('summary').innerHTML=`<span class="pill">Ayanamsa ${c.kp_ayanamsa.toFixed(6)}</span><span class="pill">Dasha ${c.current_dasha.join(' → ')}</span><span class="pill">RP ${c.ruling_planets.join(', ')}</span>`;document.getElementById('planets').innerHTML=table(c.planets,['Planet','Degree','House','Star','Sub'],p=>`<tr><td>${p.name}${p.retrograde?' ℞':''}</td><td>${p.longitude_dms}</td><td>${p.house}</td><td>${p.star_lord}</td><td>${p.sub_lord}</td></tr>`);document.getElementById('cusps').innerHTML=table(c.cusps,['Cusp','Degree','SL','Star','Sub'],q=>`<tr><td>${q.house}</td><td>${q.longitude_dms}</td><td>${q.sign_lord}</td><td>${q.star_lord}</td><td>${q.sub_lord}</td></tr>`);document.getElementById('json').textContent=JSON.stringify(c,null,2)}
async function calculate(){document.getElementById('summary').textContent='Calculating...';const r=await fetch('/api/chart',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});render(await r.json())}
async function predict(){document.getElementById('prediction').textContent='Analyzing cusp sub-lord, significators, dasha, ruling planets, and local LLM if available...';const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chart:payload(),module:val('module'),question:val('question'),use_llm:true})});const data=await r.json();document.getElementById('prediction').innerHTML=`<p><b>Verdict:</b> ${data.structured.verdict} | <b>Confidence:</b> ${data.structured.confidence_score}%</p><p><b>Cusp:</b> ${data.structured.queried_cusp}, <b>Sub Lord:</b> ${data.structured.queried_cusp_sub_lord}</p><p><b>Hits:</b> ${data.structured.primary_hits.join(', ')||'none'} | <b>Obstacles:</b> ${data.structured.obstacle_hits.join(', ')||'none'}</p><p>${data.llm.text||data.llm.warning||'Showing deterministic structured result only.'}</p><pre>${JSON.stringify(data.structured,null,2)}</pre>`}
calculate();</script></body></html>
"""

app = FastAPI(title="One File Mobile KP Astrology AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "single-file-mobile-kp"}


@app.get("/api/degree/{longitude}")
def degree(longitude: float) -> dict[str, Any]:
    return division_info(longitude)


@app.post("/api/chart")
def api_chart(req: ChartRequest) -> dict[str, Any]:
    return build_chart(req)


@app.post("/api/predict")
async def api_predict(req: PredictRequest) -> dict[str, Any]:
    chart = build_chart(req.chart)
    structured = evaluate(req.module, chart, req.question)
    llm = await local_llm(structured, req.model) if req.use_llm else {"available": False, "text": None}
    return {"structured": structured, "llm": llm}
