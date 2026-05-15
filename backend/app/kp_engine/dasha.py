from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.kp_engine.constants import DASHA_YEARS, NAKSHATRA_SPAN, VIMSHOTTARI_SEQUENCE
from app.kp_engine.nakshatra import map_lords

DAYS_PER_YEAR = 365.2425


@dataclass(frozen=True)
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: str


def _rotate(lord: str) -> list[str]:
    idx = VIMSHOTTARI_SEQUENCE.index(lord)
    return VIMSHOTTARI_SEQUENCE[idx:] + VIMSHOTTARI_SEQUENCE[:idx]


def mahadasha_schedule(moon_longitude: float, birth_time: datetime, years: float = 120.0) -> list[DashaPeriod]:
    mapping = map_lords(moon_longitude)
    nak_start = int(moon_longitude // NAKSHATRA_SPAN) * NAKSHATRA_SPAN
    elapsed_fraction = (moon_longitude - nak_start) / NAKSHATRA_SPAN
    balance_years = DASHA_YEARS[mapping.star_lord] * (1 - elapsed_fraction)
    start = birth_time.astimezone(timezone.utc)
    first_start = start - timedelta(days=(DASHA_YEARS[mapping.star_lord] - balance_years) * DAYS_PER_YEAR)

    periods: list[DashaPeriod] = []
    cursor = first_start
    horizon = start + timedelta(days=years * DAYS_PER_YEAR)
    for lord in _rotate(mapping.star_lord) * 14:
        end = cursor + timedelta(days=DASHA_YEARS[lord] * DAYS_PER_YEAR)
        if end >= start and cursor <= horizon:
            periods.append(DashaPeriod(lord, max(cursor, start), min(end, horizon), "mahadasha"))
        cursor = end
        if cursor > horizon:
            break
    return periods


def antardasha_schedule(mahadasha: DashaPeriod) -> list[DashaPeriod]:
    total_days = (mahadasha.end - mahadasha.start).total_seconds() / 86400
    cursor = mahadasha.start
    periods = []
    for lord in _rotate(mahadasha.lord):
        span_days = total_days * (DASHA_YEARS[lord] / 120.0)
        end = cursor + timedelta(days=span_days)
        periods.append(DashaPeriod(lord, cursor, end, "antardasha"))
        cursor = end
    return periods
