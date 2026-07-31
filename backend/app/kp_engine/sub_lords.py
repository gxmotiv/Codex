from __future__ import annotations

from dataclasses import dataclass

from .constants import NAKSHATRA_NAMES, NAKSHATRA_SPAN, SIGN_LORDS, VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from .utils import normalize_deg, sign_name


@dataclass(frozen=True)
class DivisionInfo:
    longitude: float
    sign: str
    sign_lord: str
    nakshatra: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    nakshatra_index: int
    pada: int


def ordered_from(lord: str) -> list[str]:
    idx = VIMSHOTTARI_ORDER.index(lord)
    return VIMSHOTTARI_ORDER[idx:] + VIMSHOTTARI_ORDER[:idx]


def star_lord_for_nakshatra(index: int) -> str:
    return VIMSHOTTARI_ORDER[index % len(VIMSHOTTARI_ORDER)]


def _sub_lord(offset_deg: float, parent_span: float, start_lord: str) -> tuple[str, float, float]:
    cursor = 0.0
    for lord in ordered_from(start_lord):
        span = parent_span * VIMSHOTTARI_YEARS[lord] / 120.0
        if offset_deg <= cursor + span + 1e-10:
            return lord, cursor, span
        cursor += span
    return ordered_from(start_lord)[-1], cursor, parent_span - cursor


def division_info(longitude: float) -> DivisionInfo:
    lon = normalize_deg(longitude)
    sign = sign_name(lon)
    nak_index = min(26, int(lon // NAKSHATRA_SPAN))
    nak_start = nak_index * NAKSHATRA_SPAN
    offset = lon - nak_start
    star_lord = star_lord_for_nakshatra(nak_index)
    sub_lord, sub_start, sub_span = _sub_lord(offset, NAKSHATRA_SPAN, star_lord)
    sub_sub_lord, _, _ = _sub_lord(offset - sub_start, sub_span, sub_lord)
    pada = int((offset / (NAKSHATRA_SPAN / 4.0))) + 1
    return DivisionInfo(
        longitude=lon,
        sign=sign,
        sign_lord=SIGN_LORDS[sign],
        nakshatra=NAKSHATRA_NAMES[nak_index],
        star_lord=star_lord,
        sub_lord=sub_lord,
        sub_sub_lord=sub_sub_lord,
        nakshatra_index=nak_index,
        pada=min(pada, 4),
    )


def kp_subdivision_table() -> list[dict]:
    rows: list[dict] = []
    for nak_index, nak_name in enumerate(NAKSHATRA_NAMES):
        star_lord = star_lord_for_nakshatra(nak_index)
        cursor = nak_index * NAKSHATRA_SPAN
        for sub_lord in ordered_from(star_lord):
            span = NAKSHATRA_SPAN * VIMSHOTTARI_YEARS[sub_lord] / 120.0
            rows.append({
                "nakshatra": nak_name,
                "star_lord": star_lord,
                "sub_lord": sub_lord,
                "start": cursor,
                "end": cursor + span,
                "span_degrees": span,
            })
            cursor += span
    return rows
