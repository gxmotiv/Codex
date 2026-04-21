from __future__ import annotations

from typing import Any

BENEFICS = {"jupiter", "venus", "mercury", "moon"}
MALEFICS = {"saturn", "mars", "rahu", "ketu", "sun"}


def _house_of_planet(chart: dict[str, Any], planet: str) -> int:
    return int(chart["positions"][planet]["rashi_index"]) + 1


def _count_in_houses(chart: dict[str, Any], planets: set[str], target_houses: set[int]) -> int:
    return sum(1 for p in planets if _house_of_planet(chart, p) in target_houses)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def interpret_chart(chart: dict[str, Any]) -> dict[str, Any]:
    """Generate a minimal, explainable System #1 interpretation output.

    This module intentionally uses deterministic heuristics with transparent scoring,
    so it can be expanded into full rule-pack/DSL evaluation later.
    """

    benefic_career = _count_in_houses(chart, BENEFICS, {10, 11, 2})
    malefic_career = _count_in_houses(chart, MALEFICS, {10, 11, 2})
    benefic_marriage = _count_in_houses(chart, BENEFICS, {7, 2, 11})
    malefic_marriage = _count_in_houses(chart, MALEFICS, {7, 2, 11})

    career_score = _clamp01(0.5 + 0.12 * benefic_career - 0.10 * malefic_career)
    marriage_score = _clamp01(0.5 + 0.12 * benefic_marriage - 0.10 * malefic_marriage)

    confidence = _clamp01(0.45 + 0.20 * abs(career_score - 0.5) + 0.20 * abs(marriage_score - 0.5))

    traces = [
        {
            "rule_id": "SYS1_CAREER_HEURISTIC_001",
            "topic": "career",
            "support_count": benefic_career,
            "obstacle_count": malefic_career,
            "score": round(career_score, 4),
        },
        {
            "rule_id": "SYS1_MARRIAGE_HEURISTIC_001",
            "topic": "marriage",
            "support_count": benefic_marriage,
            "obstacle_count": malefic_marriage,
            "score": round(marriage_score, 4),
        },
    ]

    def band(score: float) -> str:
        if score >= 0.75:
            return "strong"
        if score >= 0.6:
            return "likely"
        if score >= 0.45:
            return "conditional"
        return "weak"

    return {
        "system": "jyotish-knowledge-interpretation-system-v1",
        "topics": {
            "career": {"score": round(career_score, 4), "band": band(career_score)},
            "marriage": {"score": round(marriage_score, 4), "band": band(marriage_score)},
        },
        "confidence": round(confidence, 4),
        "trace": traces,
        "notes": [
            "Prototype rule-engine output; deterministic heuristics only.",
            "Use for system scaffolding and not as final interpretive authority.",
        ],
    }
