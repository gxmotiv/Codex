import unittest

from jyotish_engine.engine import compute_chart, norm360


class EngineTests(unittest.TestCase):
    def test_norm360(self):
        self.assertEqual(norm360(361), 1)
        self.assertEqual(norm360(-1), 359)

    def test_compute_chart_structure(self):
        payload = {
            "request_id": "test",
            "datetime_local": "1992-10-14T08:45:00",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "config": {"ayanamsha_deg": 24.0, "house_system": "whole_sign"},
        }
        result = compute_chart(payload)
        self.assertEqual(result["request_id"], "test")
        self.assertIn("sun", result["positions"])
        self.assertIn("moon", result["positions"])
        self.assertIn("ketu", result["positions"])
        self.assertEqual(len(result["houses"]), 12)
        self.assertIn("birth_mahadasha_lord", result["vimshottari_seed"])


if __name__ == "__main__":
    unittest.main()
