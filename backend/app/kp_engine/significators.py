from __future__ import annotations

from typing import Any

from .ephemeris import house_for_longitude, houses_owned_by_planet


def build_significators(planets: dict[str, dict[str, Any]], cusps: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    occupied = {name: house_for_longitude(data["longitude"], cusps) for name, data in planets.items()}
    output: dict[str, dict[str, Any]] = {}
    for planet, data in planets.items():
        star_lord = data["star_lord"]
        level1 = [occupied[star_lord]] if star_lord in occupied else []
        level2 = [occupied[planet]] if planet in occupied else []
        level3 = houses_owned_by_planet(star_lord, cusps)
        level4 = houses_owned_by_planet(planet, cusps)
        strong = sorted(set(level1 + level2))
        weak = sorted(set(level3 + level4))
        output[planet] = {
            "star_lord": star_lord,
            "levels": {"1_star": level1, "2_occupation": level2, "3_star_lord_ownership": level3, "4_planet_ownership": level4},
            "strong_houses": strong,
            "weak_houses": weak,
            "all_houses": sorted(set(strong + weak)),
            "matrix": {str(h): _level_marks(h, level1, level2, level3, level4) for h in range(1, 13)},
        }
    return output


def _level_marks(house: int, *levels: list[int]) -> list[str]:
    labels = ["L1", "L2", "L3", "L4"]
    return [labels[idx] for idx, houses in enumerate(levels) if house in houses]
