from datetime import datetime, timezone

from app.kp_engine.ayanamsa import kp_ayanamsa, tropical_to_sidereal
from app.kp_engine.dasha import antardasha_schedule, mahadasha_schedule
from app.kp_engine.nakshatra import map_lords
from app.kp_engine.placidus import placidus_cusps
from app.kp_engine.predictions import prediction_json
from app.kp_engine.significators import build_significators, house_for_longitude


def test_kp_ayanamsa_progresses_with_precession():
    assert round(kp_ayanamsa(2000), 6) == 23.85675
    assert kp_ayanamsa(2020) > kp_ayanamsa(2000)
    assert round(tropical_to_sidereal(100, 2000), 6) == 76.14325


def test_placidus_cusps_returns_twelve_normalized_values():
    cusps = placidus_cusps(datetime(1990, 1, 1, 12, tzinfo=timezone.utc), 28.6139, 77.2090)
    assert len(cusps) == 12
    assert all(0 <= cusp < 360 for cusp in cusps)


def test_sub_lord_mapping_starts_with_ketu_for_ashwini():
    mapping = map_lords(0.01)
    assert mapping.nakshatra == "Ashwini"
    assert mapping.star_lord == "Ketu"
    assert mapping.sub_lord == "Ketu"
    assert mapping.sub_sub_lord == "Ketu"
    assert mapping.pada == 1


def test_dasha_periods_are_ordered_and_antardashas_cover_parent():
    birth = datetime(1990, 1, 1, tzinfo=timezone.utc)
    periods = mahadasha_schedule(10.0, birth, years=30)
    assert periods[0].start == birth
    assert periods[0].end > periods[0].start
    antars = antardasha_schedule(periods[0])
    assert len(antars) == 9
    assert antars[0].start == periods[0].start
    assert antars[-1].end.date() == periods[0].end.date()


def test_significators_include_occupied_house_and_star_lord_houses():
    positions = {"Sun": 15.0, "Moon": 45.0, "Mars": 95.0, "Ketu": 180.0}
    cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    assert house_for_longitude(95, cusps) == 4
    significators = build_significators(positions, cusps)
    assert 1 in significators["Sun"]
    assert 4 in significators["Mars"]


def test_prediction_json_is_serializable_shape():
    birth = datetime(1990, 1, 1, tzinfo=timezone.utc)
    positions = {"Sun": 15.0, "Moon": 45.0, "Mars": 95.0, "Ketu": 180.0}
    cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    result = prediction_json("Will the project launch?", birth, positions["Moon"], positions, cusps)
    assert result["question"] == "Will the project launch?"
    assert result["active_dasha"]["level"] == "mahadasha"
    assert "significators" in result
    assert "prediction" in result
