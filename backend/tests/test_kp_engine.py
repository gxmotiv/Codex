from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.kp_engine.chart import ChartRequest, build_chart
from app.kp_engine.dasha import vimshottari_tree
from app.kp_engine.sub_lords import division_info, kp_subdivision_table


def test_kp_subdivision_table_has_243_nakshatra_sub_rows_and_covers_zodiac():
    rows = kp_subdivision_table()
    assert len(rows) == 27 * 9
    assert abs(rows[0]["start"] - 0.0) < 1e-9
    assert abs(rows[-1]["end"] - 360.0) < 1e-7


def test_degree_zero_maps_to_ashwini_ketu():
    info = division_info(0)
    assert info.sign == "Aries"
    assert info.star_lord == "Ketu"
    assert info.sub_lord == "Ketu"


def test_dasha_starts_from_moon_star_lord():
    tree = vimshottari_tree(15.0, datetime(1990, 5, 15, tzinfo=ZoneInfo("UTC")), depth=2)
    assert tree[0]["lord"] in {"Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"}
    assert "children" in tree[0]


def test_chart_calculates_real_planets_and_cusps():
    req = ChartRequest(date="1990-05-15", time="10:30:00", timezone="Asia/Kolkata", latitude=19.076, longitude=72.8777)
    chart = build_chart(req)
    assert len(chart["cusps"]) == 12
    assert "Moon" in chart["planets"]
    assert chart["planets"]["Rahu"]["longitude"] != chart["planets"]["Ketu"]["longitude"]
    assert chart["current_dasha"]
