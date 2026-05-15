from datetime import datetime

from app.kp_engine.dasha import mahadasha_schedule
from app.kp_engine.nakshatra import map_lords
from app.kp_engine.significators import build_significators


def _period_json(period) -> dict:
    return {"lord": period.lord, "start": period.start.isoformat(), "end": period.end.isoformat(), "level": period.level}


def prediction_json(question: str, birth_time: datetime, moon_longitude: float, planet_positions: dict[str, float], cusps: list[float]) -> dict:
    lords = {planet: map_lords(longitude).__dict__ for planet, longitude in planet_positions.items()}
    dashas = mahadasha_schedule(moon_longitude, birth_time, years=20)
    significators = build_significators(planet_positions, cusps)
    return {
        "question": question,
        "moon_longitude": moon_longitude,
        "active_dasha": _period_json(dashas[0]) if dashas else None,
        "significators": significators,
        "lord_mappings": lords,
        "prediction": {
            "summary": "KP judgement scaffold generated from cuspal, stellar, sub-lord, dasha, and significator factors.",
            "favorable_houses": sorted({house for houses in significators.values() for house in houses}),
            "confidence": "draft",
        },
    }
