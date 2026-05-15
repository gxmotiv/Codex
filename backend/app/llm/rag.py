from __future__ import annotations

from collections import Counter
from typing import Any

RULE_LIBRARY = [
    {"topic": "marriage", "text": "Marriage is promised when the 7th cusp sub-lord signifies 2, 7, and 11; 1, 6, 10, and 12 obstruct or deny."},
    {"topic": "career", "text": "Service is judged from 6, 2, 10, 11; business adds 7, 5, 10, 11 and partnership indications."},
    {"topic": "health", "text": "Disease is judged from 6, 8, 12; recovery from 5 and 11; first cusp sub-lord shows health promise."},
    {"topic": "property", "text": "Property purchase needs 4, 11, 12; sale uses 3, 5, 10; Mars and Saturn support construction."},
    {"topic": "foreign", "text": "Foreign travel and settlement require 3, 9, 12; the 4th house anchors to motherland and the 8th shows visa crises."},
    {"topic": "children", "text": "Children are judged through 2, 5, 11, with 5th cusp sub-lord and Jupiter as important supporting factors."},
    {"topic": "education", "text": "Education uses 4, 9, 11; higher studies add 9 and 12, with 4th and 9th cusp sub-lords decisive."},
    {"topic": "wealth", "text": "Wealth accumulation uses 2, 6, 10, 11; sudden gains use 5, 8, 11; losses are 8 and 12."},
    {"topic": "horary", "text": "Horary compares the querent first cusp sub-lord with the questioned house and confirms through ruling planets, dasha, and transit."},
]


def retrieve_rules(question: str, module: str, k: int = 3) -> list[str]:
    tokens = Counter((question + " " + module).lower().split())
    scored: list[tuple[int, dict[str, Any]]] = []
    for rule in RULE_LIBRARY:
        haystack = (rule["topic"] + " " + rule["text"]).lower().split()
        score = sum(tokens[word] for word in haystack) + (5 if rule["topic"] == module else 0)
        scored.append((score, rule))
    return [rule["text"] for score, rule in sorted(scored, key=lambda x: x[0], reverse=True)[:k]]
