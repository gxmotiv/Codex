import unittest

from jyotish_engine.engine import compute_chart, norm360
from jyotish_engine.interpretation import interpret_chart
from jyotish_engine.webapp import build_result


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "request_id": "test",
            "datetime_local": "1992-10-14T08:45:00",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "config": {"ayanamsha_deg": 24.0, "house_system": "whole_sign", "node_mode": "true"},
        }

    def test_norm360(self):
        self.assertEqual(norm360(361), 1)
        self.assertEqual(norm360(-1), 359)

    def test_compute_chart_structure(self):
        result = compute_chart(self.payload)
        self.assertEqual(result["request_id"], "test")
        self.assertIn("sun", result["positions"])
        self.assertIn("moon", result["positions"])
        self.assertIn("ketu", result["positions"])
        self.assertEqual(len(result["houses"]), 12)
        self.assertIn("D9", result["vargas"])
        self.assertIn("birth_mahadasha_lord", result["vimshottari_seed"])

    def test_interpretation_structure(self):
        chart = compute_chart(self.payload)
        interpretation = interpret_chart(chart)
        self.assertEqual(interpretation["system"], "vedic-interpretation-predictive-system-v1")
        self.assertIn("knowledge_base", interpretation)
        self.assertIn("synthesis", interpretation)
        self.assertIn("yoga_detection", interpretation)
        self.assertIn("predictive_engine", interpretation)
        self.assertIn("remedial_logic", interpretation)
        self.assertGreaterEqual(interpretation["confidence"], 0)
        self.assertLessEqual(interpretation["confidence"], 1)

    def test_webapp_build_result(self):
        result = build_result(self.payload)
        self.assertIn("chart", result)
        self.assertIn("interpretation", result)
        self.assertIn("flow", result["interpretation"])


if __name__ == "__main__":
    unittest.main()
