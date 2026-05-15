from __future__ import annotations

import math
from datetime import datetime
from zoneinfo import ZoneInfo

from .constants import SIGN_NAMES


def normalize_deg(value: float) -> float:
    return value % 360.0


def sign_index(longitude: float) -> int:
    return int(normalize_deg(longitude) // 30)


def sign_name(longitude: float) -> str:
    return SIGN_NAMES[sign_index(longitude)]


def dms(longitude: float) -> str:
    lon = normalize_deg(longitude)
    sign = sign_name(lon)
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
    return f"{sign} {deg:02d}°{minutes:02d}'{seconds:02d}\""


def parse_local_datetime(date: str, time: str, timezone: str) -> datetime:
    return datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=ZoneInfo(timezone))


def circular_between(start: float, end: float, point: float) -> bool:
    start = normalize_deg(start)
    end = normalize_deg(end)
    point = normalize_deg(point)
    if start <= end:
        return start <= point < end
    return point >= start or point < end


def angular_distance(a: float, b: float) -> float:
    delta = abs(normalize_deg(a) - normalize_deg(b)) % 360
    return min(delta, 360 - delta)


def years_to_days(years: float) -> float:
    return years * 365.2425
