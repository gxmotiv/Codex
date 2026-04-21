import unittest

from jyotish_engine.engine import compute_chart, norm360
from jyotish_engine.interpretation import interpret_chart


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "request_id": "test",
            "datetime_local": "1992-10-14T08:45:00",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "config": {"ayanamsha_deg": 24.0, "house_system": "whole_sign"},
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
        self.assertIn("birth_mahadasha_lord", result["vimshottari_seed"])

    def test_interpretation_structure(self):
        chart = compute_chart(self.payload)
        interpretation = interpret_chart(chart)
        self.assertEqual(interpretation["system"], "jyotish-knowledge-interpretation-system-v1")
        self.assertIn("career", interpretation["topics"])
        self.assertIn("marriage", interpretation["topics"])
        self.assertGreaterEqual(interpretation["confidence"], 0)
        self.assertLessEqual(interpretation["confidence"], 1)


if __name__ == "__main__":
    unittest.main()
