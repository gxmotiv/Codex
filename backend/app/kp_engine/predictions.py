from __future__ import annotations

from typing import Any

MODULE_RULES = {
    "marriage": {"primary": [2, 7, 11], "supporting": [5, 1], "obstacles": [1, 6, 10, 12, 4], "cusp": 7},
    "career": {"primary": [6, 2, 10, 11], "business": [7, 2, 5, 10, 11], "obstacles": [8, 12], "cusp": 10},
    "health": {"primary": [5, 11], "obstacles": [6, 8, 12], "cusp": 1},
    "property": {"primary": [4, 11, 12], "sale": [3, 5, 10], "obstacles": [8], "cusp": 4},
    "foreign": {"primary": [3, 9, 12], "supporting": [11], "obstacles": [4, 8], "cusp": 12},
    "children": {"primary": [2, 5, 11], "obstacles": [1, 4, 10, 12], "cusp": 5},
    "education": {"primary": [4, 9, 11], "higher": [9, 12], "obstacles": [8], "cusp": 4},
    "wealth": {"primary": [2, 6, 10, 11], "sudden": [5, 8, 11], "obstacles": [8, 12], "cusp": 2},
    "longevity": {"primary": [1, 8], "maraka": [2, 7], "cusp": 8},
    "horary": {"primary": [1, 11], "obstacles": [8, 12], "cusp": 1},
}

RULE_TEXT = {
    "marriage": ["7th cusp sub-lord must signify 2, 7, or 11 for marriage promise.", "Dasha lords supporting 2, 7, and 11 improve timing; 1, 6, 10, 12 show obstacles."],
    "foreign": ["Foreign settlement is judged from 3, 9, 12 with 12th cusp as final decider.", "Strong 4th house emphasis pulls back to motherland; 8th can show visa obstacles."],
}


def evaluate_module(module: str, chart: dict[str, Any], question: str = "") -> dict[str, Any]:
    rules = MODULE_RULES[module]
    cusp = chart["cusps"][str(rules["cusp"])] if isinstance(next(iter(chart["cusps"].keys())), str) else chart["cusps"][rules["cusp"]]
    sub_lord = cusp["sub_lord"]
    sub_sig = chart["significators"].get(sub_lord, {})
    all_houses = set(sub_sig.get("all_houses", []))
    primary = set(rules.get("primary", []))
    obstacles = set(rules.get("obstacles", []))
    primary_hits = sorted(all_houses & primary)
    obstacle_hits = sorted(all_houses & obstacles)
    score = min(100, max(0, 35 + 15 * len(primary_hits) - 8 * len(obstacle_hits)))
    verdict = "supportive" if len(primary_hits) >= 2 else "mixed" if primary_hits else "weak_or_denied"
    dasha_path = chart.get("current_dasha", [])
    dasha_support = {lord: sorted(set(chart["significators"].get(lord, {}).get("all_houses", [])) & primary) for lord in dasha_path}
    return {
        "module": module,
        "question": question,
        "queried_cusp": rules["cusp"],
        "queried_cusp_sub_lord": sub_lord,
        "sub_lord_significations": sub_sig,
        "primary_houses": sorted(primary),
        "obstacle_houses": sorted(obstacles),
        "primary_hits": primary_hits,
        "obstacle_hits": obstacle_hits,
        "current_dasha": dasha_path,
        "dasha_support": dasha_support,
        "ruling_planets": chart.get("ruling_planets", {}).get("ruling_planets", []),
        "confidence_score": score,
        "verdict": verdict,
        "kp_rules": RULE_TEXT.get(module, [f"Judge {module} from cusp {rules['cusp']} and houses {sorted(primary)}."]),
    }
