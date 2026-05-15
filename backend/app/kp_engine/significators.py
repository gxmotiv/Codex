from collections import defaultdict

from app.kp_engine.nakshatra import map_lords


def house_for_longitude(longitude: float, cusps: list[float]) -> int:
    ordered = [(cusp % 360.0, index + 1) for index, cusp in enumerate(cusps)]
    ordered.sort()
    selected = ordered[-1][1]
    for cusp, house in ordered:
        if longitude >= cusp:
            selected = house
        else:
            break
    return selected


def build_significators(planet_positions: dict[str, float], cusps: list[float]) -> dict[str, list[int]]:
    """Map each planet to KP houses signified by occupation and star-lord linkage."""
    occupied = {planet: house_for_longitude(lon, cusps) for planet, lon in planet_positions.items()}
    by_star_lord: dict[str, set[int]] = defaultdict(set)
    for planet, longitude in planet_positions.items():
        by_star_lord[map_lords(longitude).star_lord].add(occupied[planet])

    significators = {}
    for planet, house in occupied.items():
        houses = {house}
        houses.update(by_star_lord.get(planet, set()))
        significators[planet] = sorted(houses)
    return significators
