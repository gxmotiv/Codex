from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    import swisseph as swe
except ImportError as exc:  # pragma: no cover
    swe = None
    SWISSEPH_IMPORT_ERROR = exc
else:
    SWISSEPH_IMPORT_ERROR = None

from .constants import OUTER_PLANETS, PLANETS, SIGN_LORDS
from .sub_lords import division_info
from .utils import circular_between, dms, normalize_deg, sign_name

SWISS_PLANETS = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    "Rahu": 11,
}


def _require_swe():
    if swe is None:  # pragma: no cover
        raise RuntimeError(f"pyswisseph is required: {SWISSEPH_IMPORT_ERROR}")


def julian_day(dt: datetime) -> float:
    _require_swe()
    utc = dt.astimezone(timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3_600_000_000
    return swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)


def set_kp_ayanamsa() -> None:
    _require_swe()
    sidm_kp = getattr(swe, "SIDM_KRISHNAMURTI", None)
    if sidm_kp is None:
        sidm_kp = getattr(swe, "SIDM_KRISHNAMURTI_VP291", swe.SIDM_LAHIRI)
    swe.set_sid_mode(sidm_kp, 0, 0)


def ayanamsa(jd_ut: float) -> float:
    set_kp_ayanamsa()
    return float(swe.get_ayanamsa_ut(jd_ut))


def calculate_planets(dt: datetime, latitude: float, longitude: float, topocentric: bool, include_outer: bool = True) -> dict[str, dict[str, Any]]:
    _require_swe()
    set_kp_ayanamsa()
    jd = julian_day(dt)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    if topocentric:
        swe.set_topo(longitude, latitude, 0)
        flags |= swe.FLG_TOPOCTR
    names = PLANETS + (OUTER_PLANETS if include_outer else [])
    out: dict[str, dict[str, Any]] = {}
    rahu_lon = None
    for name in names:
        if name == "Ketu":
            if rahu_lon is None:
                continue
            lon = normalize_deg(rahu_lon + 180)
            lat = 0.0
            speed = 0.0
        else:
            values, _ = swe.calc_ut(jd, SWISS_PLANETS[name], flags)
            lon, lat, _dist, speed, *_ = values
            if name == "Rahu":
                rahu_lon = lon
        info = division_info(lon)
        out[name] = {
            "name": name,
            "longitude": normalize_deg(lon),
            "longitude_dms": dms(lon),
            "latitude": lat,
            "speed": speed,
            "retrograde": speed < 0,
            "sign_lord": info.sign_lord,
            "star_lord": info.star_lord,
            "sub_lord": info.sub_lord,
            "sub_sub_lord": info.sub_sub_lord,
            "nakshatra": info.nakshatra,
        }
    return out


def calculate_cusps(dt: datetime, latitude: float, longitude: float) -> dict[int, dict[str, Any]]:
    _require_swe()
    set_kp_ayanamsa()
    jd = julian_day(dt)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    output: dict[int, dict[str, Any]] = {}
    for house in range(1, 13):
        lon = normalize_deg(cusps[house - 1])
        info = division_info(lon)
        output[house] = {
            "house": house,
            "longitude": lon,
            "longitude_dms": dms(lon),
            "sign": info.sign,
            "sign_lord": info.sign_lord,
            "star_lord": info.star_lord,
            "sub_lord": info.sub_lord,
            "sub_sub_lord": info.sub_sub_lord,
            "nakshatra": info.nakshatra,
        }
    return output


def house_for_longitude(longitude: float, cusps: dict[int, dict[str, Any]]) -> int:
    ordered = [cusps[i]["longitude"] for i in range(1, 13)]
    for idx in range(12):
        start = ordered[idx]
        end = ordered[(idx + 1) % 12]
        if circular_between(start, end, longitude):
            return idx + 1
    return 12


def houses_owned_by_planet(planet: str, cusps: dict[int, dict[str, Any]]) -> list[int]:
    return [house for house, cusp in cusps.items() if SIGN_LORDS[sign_name(cusp["longitude"])] == planet]
