from dataclasses import dataclass

from app.kp_engine.ayanamsa import normalize_degrees
from app.kp_engine.constants import DASHA_YEARS, NAKSHATRA_LORDS, NAKSHATRA_NAMES, NAKSHATRA_SPAN, VIMSHOTTARI_SEQUENCE


@dataclass(frozen=True)
class LordMapping:
    nakshatra: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    pada: int


def _sequence_from(lord: str) -> list[str]:
    index = VIMSHOTTARI_SEQUENCE.index(lord)
    return VIMSHOTTARI_SEQUENCE[index:] + VIMSHOTTARI_SEQUENCE[:index]


def _lord_for_fraction(start_lord: str, fraction: float) -> tuple[str, float, float]:
    cursor = 0.0
    for lord in _sequence_from(start_lord):
        span = DASHA_YEARS[lord] / 120.0
        if fraction < cursor + span or lord == _sequence_from(start_lord)[-1]:
            local_fraction = (fraction - cursor) / span
            return lord, local_fraction, span
        cursor += span
    return start_lord, 0.0, 1.0


def map_lords(longitude: float) -> LordMapping:
    lon = normalize_degrees(longitude)
    nak_index = int(lon // NAKSHATRA_SPAN)
    within = (lon - nak_index * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    star_lord = NAKSHATRA_LORDS[nak_index]
    sub_lord, sub_fraction, _span = _lord_for_fraction(star_lord, within)
    sub_sub_lord, _sub_sub_fraction, _sub_span = _lord_for_fraction(sub_lord, sub_fraction)
    pada = int(within * 4) + 1
    return LordMapping(NAKSHATRA_NAMES[nak_index], star_lord, sub_lord, sub_sub_lord, min(pada, 4))
