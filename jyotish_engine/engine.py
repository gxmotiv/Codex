from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import floor
from zoneinfo import ZoneInfo

PLANETS = {
    "sun": (280.460, 0.9856474),
    "moon": (218.316, 13.176396),
    "mars": (355.433, 0.524039),
    "mercury": (252.251, 4.092385),
    "jupiter": (34.351, 0.083086),
    "venus": (181.979, 1.602130),
    "saturn": (50.077, 0.033459),
    "rahu": (0.0, -0.0529539),
}

VIMSHOTTARI_ORDER = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
VIMSHOTTARI_YEARS = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}

MOVABLE = {0, 3, 6, 9}
FIXED = {1, 4, 7, 10}
DUAL = {2, 5, 8, 11}


@dataclass
class ChartConfig:
    ayanamsha_deg: float = 24.0
    house_system: str = "whole_sign"
    node_mode: str = "true"


def norm360(value: float) -> float:
    return value % 360.0


def julian_day(dt_utc: datetime) -> float:
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day + (dt_utc.hour + (dt_utc.minute + dt_utc.second / 60) / 60) / 24
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day + b - 1524.5


def parse_local_to_utc(local_iso: str, tz_name: str) -> datetime:
    local_dt = datetime.fromisoformat(local_iso)
    localized = local_dt.replace(tzinfo=ZoneInfo(tz_name))
    return localized.astimezone(timezone.utc)


def mean_longitude(jd: float, base_deg: float, motion_deg_per_day: float) -> float:
    d = jd - 2451545.0
    return norm360(base_deg + motion_deg_per_day * d)


def _divisional_rashi(longitude_sidereal: float, division: int) -> int:
    base_rashi = int(longitude_sidereal // 30)
    intra = longitude_sidereal % 30
    part = int(intra // (30 / division))

    if division == 9:
        if base_rashi in MOVABLE:
            start = base_rashi
        elif base_rashi in FIXED:
            start = (base_rashi + 8) % 12
        else:
            start = (base_rashi + 4) % 12
        return (start + part) % 12

    return (base_rashi + part) % 12


def _build_vargas(positions: dict) -> dict:
    vargas: dict[str, dict[str, int]] = {"D1": {}, "D7": {}, "D9": {}, "D10": {}}
    for body, info in positions.items():
        sid = info["longitude_sidereal_deg"]
        vargas["D1"][body] = info["rashi_index"]
        vargas["D7"][body] = _divisional_rashi(sid, 7)
        vargas["D9"][body] = _divisional_rashi(sid, 9)
        vargas["D10"][body] = _divisional_rashi(sid, 10)
    return vargas


def build_positions(jd_ut: float, ayanamsha_deg: float, node_mode: str = "true") -> dict:
    positions = {}
    for body, (base, motion) in PLANETS.items():
        trop = mean_longitude(jd_ut, base, motion)
        if body == "rahu" and node_mode == "mean":
            trop = norm360(trop - 1.2)
        sid = norm360(trop - ayanamsha_deg)
        positions[body] = {
            "longitude_tropical_deg": round(trop, 6),
            "longitude_sidereal_deg": round(sid, 6),
            "rashi_index": int(sid // 30),
            "nakshatra_index": int(sid // (360 / 27)),
            "pada_index": int((sid % (360 / 27)) // (360 / 108)),
        }
    positions["ketu"] = {
        "longitude_tropical_deg": round(norm360(positions["rahu"]["longitude_tropical_deg"] + 180), 6),
        "longitude_sidereal_deg": round(norm360(positions["rahu"]["longitude_sidereal_deg"] + 180), 6),
        "rashi_index": int(norm360(positions["rahu"]["longitude_sidereal_deg"] + 180) // 30),
        "nakshatra_index": int(norm360(positions["rahu"]["longitude_sidereal_deg"] + 180) // (360 / 27)),
        "pada_index": int((norm360(positions["rahu"]["longitude_sidereal_deg"] + 180) % (360 / 27)) // (360 / 108)),
    }
    return positions


def whole_sign_houses(asc_sid_deg: float) -> dict:
    asc_sign = int(asc_sid_deg // 30)
    return {f"house_{h}": int((asc_sign + h - 1) % 12) for h in range(1, 13)}


def approximate_ascendant(jd_ut: float, longitude: float, ayanamsha_deg: float) -> float:
    d = jd_ut - 2451545.0
    gmst = norm360(280.46061837 + 360.98564736629 * d)
    lst = norm360(gmst + longitude)
    return norm360(lst - ayanamsha_deg)


def vimshottari_seed(moon_sid_deg: float) -> dict:
    nak = int(moon_sid_deg // (360 / 27))
    lord = VIMSHOTTARI_ORDER[nak % 9]
    frac = (moon_sid_deg % (360 / 27)) / (360 / 27)
    balance_years = (1 - frac) * VIMSHOTTARI_YEARS[lord]
    return {
        "birth_nakshatra_index": nak,
        "birth_mahadasha_lord": lord,
        "balance_years": round(balance_years, 6),
    }


def compute_chart(payload: dict) -> dict:
    config = ChartConfig(
        ayanamsha_deg=float(payload.get("config", {}).get("ayanamsha_deg", 24.0)),
        house_system=payload.get("config", {}).get("house_system", "whole_sign"),
        node_mode=payload.get("config", {}).get("node_mode", "true"),
    )
    utc_dt = parse_local_to_utc(payload["datetime_local"], payload["timezone"])
    jd_ut = julian_day(utc_dt)
    positions = build_positions(jd_ut, config.ayanamsha_deg, config.node_mode)

    asc_deg = approximate_ascendant(jd_ut, float(payload["longitude"]), config.ayanamsha_deg)
    houses = whole_sign_houses(asc_deg)

    return {
        "request_id": payload.get("request_id", "local-run"),
        "meta": {
            "engine": "offline-prototype",
            "ayanamsha_deg": config.ayanamsha_deg,
            "house_system": config.house_system,
            "node_mode": config.node_mode,
        },
        "time": {
            "utc": utc_dt.isoformat(),
            "jd_ut": round(jd_ut, 6),
        },
        "positions": positions,
        "houses": houses,
        "vargas": _build_vargas(positions),
        "ascendant_sidereal_deg": round(asc_deg, 6),
        "vimshottari_seed": vimshottari_seed(positions["moon"]["longitude_sidereal_deg"]),
    }
