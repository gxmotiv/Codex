from datetime import datetime, timezone

import swisseph as swe

from app.kp_engine.ayanamsa import tropical_to_sidereal

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}


def decimal_year(moment: datetime) -> float:
    utc = moment.astimezone(timezone.utc)
    start = datetime(utc.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(utc.year + 1, 1, 1, tzinfo=timezone.utc)
    return utc.year + ((utc - start).total_seconds() / (end - start).total_seconds())


def julian_day(moment: datetime) -> float:
    utc = moment.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)


def planet_positions(moment: datetime) -> dict[str, float]:
    jd = julian_day(moment)
    year = decimal_year(moment)
    positions = {}
    for name, planet_id in PLANETS.items():
        result, _flags = swe.calc_ut(jd, planet_id)
        positions[name] = tropical_to_sidereal(result[0], year)
    positions["Ketu"] = (positions["Rahu"] + 180.0) % 360.0
    return positions
