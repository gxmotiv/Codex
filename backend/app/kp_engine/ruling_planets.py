from __future__ import annotations

from datetime import datetime
from typing import Any

from .constants import WEEKDAY_LORDS
from .ephemeris import calculate_cusps, calculate_planets


def calculate_ruling_planets(dt: datetime, latitude: float, longitude: float) -> dict[str, Any]:
    cusps = calculate_cusps(dt, latitude, longitude)
    planets = calculate_planets(dt, latitude, longitude, topocentric=True, include_outer=False)
    asc = cusps[1]
    moon = planets["Moon"]
    day_lord = WEEKDAY_LORDS[dt.weekday()]
    ordered = [asc["sign_lord"], asc["star_lord"], moon["sign_lord"], moon["star_lord"], day_lord]
    return {
        "ascendant_sign_lord": asc["sign_lord"],
        "ascendant_star_lord": asc["star_lord"],
        "moon_sign_lord": moon["sign_lord"],
        "moon_star_lord": moon["star_lord"],
        "day_lord": day_lord,
        "ruling_planets": list(dict.fromkeys(ordered)),
    }
