from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GOLDEN_PATH = Path(__file__).resolve().parents[3] / "data" / "golden_charts.json"


def load_golden_dataset() -> list[dict[str, Any]]:
    if not GOLDEN_PATH.exists():
        return []
    return json.loads(GOLDEN_PATH.read_text())
