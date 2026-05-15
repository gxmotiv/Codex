from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .dasha import current_dasha, vimshottari_tree
from .ephemeris import ayanamsa, calculate_cusps, calculate_planets, house_for_longitude, julian_day
from .ruling_planets import calculate_ruling_planets
from .significators import build_significators
from .utils import parse_local_datetime


class ChartRequest(BaseModel):
    name: str = "Native"
    date: str = Field(examples=["1990-05-15"])
    time: str = Field(examples=["10:30:00"])
    timezone: str = Field(default="Asia/Kolkata")
    latitude: float = Field(examples=[19.0760])
    longitude: float = Field(examples=[72.8777])
    topocentric: bool = True
    include_outer: bool = True


def build_chart(req: ChartRequest, at: datetime | None = None) -> dict[str, Any]:
    birth_dt = parse_local_datetime(req.date, req.time, req.timezone)
    jd = julian_day(birth_dt)
    cusps = calculate_cusps(birth_dt, req.latitude, req.longitude)
    planets = calculate_planets(birth_dt, req.latitude, req.longitude, req.topocentric, req.include_outer)
    for planet in planets.values():
        planet["house"] = house_for_longitude(planet["longitude"], cusps)
    sigs = build_significators(planets, cusps)
    tree = vimshottari_tree(planets["Moon"]["longitude"], birth_dt, depth=4)
    now = at or datetime.now(tz=birth_dt.tzinfo)
    rp = calculate_ruling_planets(now, req.latitude, req.longitude)
    return {
        "input": req.model_dump(),
        "julian_day": jd,
        "kp_ayanamsa": ayanamsa(jd),
        "planets": planets,
        "cusps": cusps,
        "significators": sigs,
        "dasha_tree": tree,
        "current_dasha": current_dasha(tree, now),
        "ruling_planets": rp,
    }
