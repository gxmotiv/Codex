from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .constants import NAKSHATRA_SPAN, VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from .sub_lords import division_info, ordered_from
from .utils import years_to_days


def _periods(start: datetime, lord_order: list[str], total_years: float, depth: int) -> list[dict[str, Any]]:
    cursor = start
    rows = []
    for lord in lord_order:
        years = total_years * VIMSHOTTARI_YEARS[lord] / 120.0
        end = cursor + timedelta(days=years_to_days(years))
        row = {"lord": lord, "start": cursor.isoformat(), "end": end.isoformat(), "years": years}
        if depth > 1:
            row["children"] = _periods(cursor, ordered_from(lord), years, depth - 1)
        rows.append(row)
        cursor = end
    return rows


def vimshottari_tree(moon_longitude: float, birth_dt: datetime, depth: int = 4) -> list[dict[str, Any]]:
    info = division_info(moon_longitude)
    nak_start = info.nakshatra_index * NAKSHATRA_SPAN
    elapsed = moon_longitude - nak_start
    remaining_fraction = max(0.0, (NAKSHATRA_SPAN - elapsed) / NAKSHATRA_SPAN)
    first_lord = info.star_lord
    first_years = VIMSHOTTARI_YEARS[first_lord] * remaining_fraction
    start = birth_dt
    first_end = start + timedelta(days=years_to_days(first_years))
    first = {"lord": first_lord, "start": start.isoformat(), "end": first_end.isoformat(), "years": first_years}
    if depth > 1:
        first["children"] = _periods(start, ordered_from(first_lord), first_years, depth - 1)
    rows = [first]
    cursor = first_end
    for lord in ordered_from(first_lord)[1:] + ordered_from(first_lord)[:1]:
        years = VIMSHOTTARI_YEARS[lord]
        end = cursor + timedelta(days=years_to_days(years))
        row = {"lord": lord, "start": cursor.isoformat(), "end": end.isoformat(), "years": years}
        if depth > 1:
            row["children"] = _periods(cursor, ordered_from(lord), years, depth - 1)
        rows.append(row)
        cursor = end
    return rows


def current_dasha(tree: list[dict[str, Any]], at: datetime) -> list[str]:
    result: list[str] = []
    rows = tree
    while rows:
        found = None
        for row in rows:
            if datetime.fromisoformat(row["start"]) <= at < datetime.fromisoformat(row["end"]):
                found = row
                break
        if not found:
            break
        result.append(found["lord"])
        rows = found.get("children", [])
    return result
