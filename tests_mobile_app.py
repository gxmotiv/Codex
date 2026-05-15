from __future__ import annotations

from fastapi.testclient import TestClient

from mobile_kp_app import app, build_chart, ChartRequest, division_info


def test_mobile_app_serves_html_and_health():
    client = TestClient(app)
    assert "Mobile KP Astrology AI" in client.get("/").text
    assert client.get("/health").json()["status"] == "ok"


def test_mobile_single_file_chart_and_prediction_api():
    client = TestClient(app)
    chart_payload = {"date": "1990-05-15", "time": "10:30:00", "timezone": "Asia/Kolkata", "latitude": 19.076, "longitude": 72.8777}
    chart = client.post("/api/chart", json=chart_payload).json()
    assert len(chart["cusps"]) == 12
    assert "Moon" in chart["planets"]
    response = client.post("/api/predict", json={"chart": chart_payload, "module": "marriage", "use_llm": False}).json()
    assert response["structured"]["module"] == "marriage"


def test_mobile_single_file_core_helpers():
    assert division_info(0)["star_lord"] == "Ketu"
    chart = build_chart(ChartRequest())
    assert chart["current_dasha"]
