from datetime import datetime

import swisseph as swe

from app.kp_engine.ayanamsa import tropical_to_sidereal
from app.kp_engine.swisseph import decimal_year, julian_day


def placidus_cusps(moment: datetime, latitude: float, longitude: float) -> list[float]:
    """Return 12 sidereal Placidus house cusps in zodiacal degrees."""
    cusps, _ascmc = swe.houses_ex(julian_day(moment), latitude, longitude, b"P")
    year = decimal_year(moment)
    return [tropical_to_sidereal(cusp, year) for cusp in cusps[:12]]
