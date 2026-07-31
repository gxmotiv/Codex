from __future__ import annotations

from typing import Any

RASHI_NAMES = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

SIGN_ATTRS = {
    0: {"modality": "movable", "element": "fire"},
    1: {"modality": "fixed", "element": "earth"},
    2: {"modality": "dual", "element": "air"},
    3: {"modality": "movable", "element": "water"},
    4: {"modality": "fixed", "element": "fire"},
    5: {"modality": "dual", "element": "earth"},
    6: {"modality": "movable", "element": "air"},
    7: {"modality": "fixed", "element": "water"},
    8: {"modality": "dual", "element": "fire"},
    9: {"modality": "movable", "element": "earth"},
    10: {"modality": "fixed", "element": "air"},
    11: {"modality": "dual", "element": "water"},
}

KARAKAS = {
    "sun": ["soul", "father", "authority"],
    "moon": ["mind", "mother", "emotions"],
    "mars": ["energy", "siblings", "conflict"],
    "mercury": ["intellect", "speech", "trade"],
    "jupiter": ["wisdom", "dharma", "teachers"],
    "venus": ["relationships", "arts", "comforts"],
    "saturn": ["discipline", "delay", "karma"],
    "rahu": ["obsession", "innovation", "foreign"],
    "ketu": ["detachment", "moksha", "past-karma"],
}

BHAVAS = {
    1: "self and vitality",
    2: "family and wealth",
    3: "effort and communication",
    4: "home and emotional base",
    5: "intelligence and children",
    6: "disease and service",
    7: "partnership and marriage",
    8: "transformation and longevity",
    9: "dharma and higher learning",
    10: "career and public karma",
    11: "gains and networks",
    12: "loss and liberation",
}

SIGN_LORD = {
    0: "mars",
    1: "venus",
    2: "mercury",
    3: "moon",
    4: "sun",
    5: "mercury",
    6: "venus",
    7: "mars",
    8: "jupiter",
    9: "saturn",
    10: "saturn",
    11: "jupiter",
}

EXALTATION = {"sun": 0, "moon": 1, "mars": 9, "mercury": 5, "jupiter": 3, "venus": 11, "saturn": 6}
DEBILITATION = {"sun": 6, "moon": 7, "mars": 3, "mercury": 11, "jupiter": 9, "venus": 5, "saturn": 0}
OWN_SIGNS = {
    "sun": {4},
    "moon": {3},
    "mars": {0, 7},
    "mercury": {2, 5},
    "jupiter": {8, 11},
    "venus": {1, 6},
    "saturn": {9, 10},
}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _planet_house(chart: dict[str, Any], planet: str) -> int:
    asc_sign = chart["houses"]["house_1"]
    sign = chart["positions"][planet]["rashi_index"]
    return ((sign - asc_sign) % 12) + 1


def _house_lords(asc_sign: int) -> dict[int, str]:
    return {h: SIGN_LORD[(asc_sign + h - 1) % 12] for h in range(1, 13)}


def _functional_nature(asc_sign: int) -> dict[str, str]:
    lords = _house_lords(asc_sign)
    planet_houses: dict[str, list[int]] = {}
    for house, lord in lords.items():
        planet_houses.setdefault(lord, []).append(house)

    result = {}
    for planet, houses in planet_houses.items():
        if any(h in {6, 8, 12} for h in houses):
            result[planet] = "functional_malefic"
        elif any(h in {1, 5, 9} for h in houses):
            result[planet] = "functional_benefic"
        else:
            result[planet] = "neutral"
    return result


def _dignity(planet: str, sign: int) -> str:
    if planet in EXALTATION and sign == EXALTATION[planet]:
        return "exalted"
    if planet in DEBILITATION and sign == DEBILITATION[planet]:
        return "debilitated"
    if sign in OWN_SIGNS.get(planet, set()):
        return "own_sign"
    return "ordinary"


def _dignity_score(status: str) -> float:
    return {"exalted": 1.0, "own_sign": 0.8, "ordinary": 0.55, "debilitated": 0.3}[status]


def _connected(sign_a: int, sign_b: int) -> bool:
    return sign_a == sign_b


def _kendra_from(reference_sign: int, target_sign: int) -> bool:
    return ((target_sign - reference_sign) % 12) in {0, 3, 6, 9}


def _yoga_detection(chart: dict[str, Any], lords: dict[int, str]) -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []

    kendra_lords = {lords[h] for h in [1, 4, 7, 10]}
    trikona_lords = {lords[h] for h in [1, 5, 9]}
    for k_lord in kendra_lords:
        for t_lord in trikona_lords:
            if _connected(chart["positions"][k_lord]["rashi_index"], chart["positions"][t_lord]["rashi_index"]):
                yogas.append({"name": "raja_yoga", "via": [k_lord, t_lord]})
                break

    wealth_lords = {lords[2], lords[11]}
    fortune_lords = {lords[5], lords[9]}
    for w_lord in wealth_lords:
        for f_lord in fortune_lords:
            if _connected(chart["positions"][w_lord]["rashi_index"], chart["positions"][f_lord]["rashi_index"]):
                yogas.append({"name": "dhana_yoga", "via": [w_lord, f_lord]})
                break

    moon_sign = chart["positions"]["moon"]["rashi_index"]
    jupiter_sign = chart["positions"]["jupiter"]["rashi_index"]
    if _kendra_from(moon_sign, jupiter_sign):
        yogas.append({"name": "gajakesari_yoga", "via": ["moon", "jupiter"]})

    return yogas


def _varga_validation(chart: dict[str, Any]) -> list[dict[str, str]]:
    validations: list[dict[str, str]] = []
    for planet in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
        d1_status = _dignity(planet, chart["vargas"]["D1"][planet])
        d9_status = _dignity(planet, chart["vargas"]["D9"][planet])
        if _dignity_score(d1_status) >= 0.8 and _dignity_score(d9_status) <= 0.55:
            validations.append({"planet": planet, "status": "false_promise"})
        elif _dignity_score(d1_status) <= 0.55 and _dignity_score(d9_status) >= 0.8:
            validations.append({"planet": planet, "status": "hidden_gem"})
    return validations


def _predictive_signals(chart: dict[str, Any]) -> dict[str, Any]:
    dasha_lord = chart["vimshottari_seed"]["birth_mahadasha_lord"]
    ad_lord = "jupiter" if dasha_lord != "jupiter" else "venus"

    asc_sign = chart["houses"]["house_1"]
    jupiter_sign = chart["positions"]["jupiter"]["rashi_index"]
    jupiter_trigger = ((jupiter_sign - asc_sign) % 12) == 6  # 7th house from lagna

    themes = []
    if dasha_lord in {"venus", "jupiter", "moon"}:
        themes.append("relationship/family activation")
    if dasha_lord in {"saturn", "sun", "mars"}:
        themes.append("career-duty activation")
    if jupiter_trigger:
        themes.append("transit trigger on partnership axis")

    return {
        "formula": "prediction = mahadasha + antardasha + transit_trigger",
        "mahadasha_lord": dasha_lord,
        "antardasha_lord": ad_lord,
        "transit_flags": {"jupiter_7th_from_lagna": jupiter_trigger},
        "themes": themes or ["no strong trigger alignment yet"],
    }


def _remedies(chart: dict[str, Any]) -> list[dict[str, str]]:
    remedies = []
    for planet in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
        status = _dignity(planet, chart["positions"][planet]["rashi_index"])
        if status == "debilitated":
            remedies.append(
                {
                    "planet": planet,
                    "gemstone_logic": "only if functional benefic and after expert validation",
                    "mantra_logic": f"daily beeja mantra discipline for {planet}",
                    "charity_logic": f"service aligned to {planet} karakatwa",
                }
            )
    return remedies


def interpret_chart(chart: dict[str, Any]) -> dict[str, Any]:
    asc_sign = chart["houses"]["house_1"]
    lords = _house_lords(asc_sign)
    functional = _functional_nature(asc_sign)

    placement = {}
    dignity = {}
    for planet, info in chart["positions"].items():
        house = _planet_house(chart, planet)
        sign = info["rashi_index"]
        placement[planet] = {
            "planet": planet,
            "karakas": KARAKAS.get(planet, []),
            "sign": RASHI_NAMES[sign],
            "sign_attributes": SIGN_ATTRS[sign],
            "house": house,
            "bhava_theme": BHAVAS[house],
        }
        dignity_status = _dignity(planet, sign)
        dignity[planet] = {
            "status": dignity_status,
            "score": round(_dignity_score(dignity_status), 2),
        }

    yogas = _yoga_detection(chart, lords)
    varga_flags = _varga_validation(chart)
    predictive = _predictive_signals(chart)
    remedies = _remedies(chart)

    base_confidence = 0.55 + min(0.2, 0.02 * len(yogas))
    base_confidence -= 0.02 * len([f for f in varga_flags if f["status"] == "false_promise"])
    confidence = _clamp01(base_confidence)

    return {
        "system": "vedic-interpretation-predictive-system-v1",
        "knowledge_base": {
            "karakas": KARAKAS,
            "bhavas": BHAVAS,
        },
        "synthesis": {
            "functional_nature": functional,
            "placement": placement,
            "dignity": dignity,
        },
        "yoga_detection": yogas,
        "varga_validation": varga_flags,
        "predictive_engine": predictive,
        "remedial_logic": remedies,
        "confidence": round(confidence, 4),
        "flow": "input -> sutra_filter -> dignity -> yoga -> varga_validation -> timing -> interpretation",
        "notes": [
            "System #1 uses explicit rule scaffolding and traceable synthesis.",
            "This prototype is deterministic and designed for expansion into classical sutra packs.",
        ],
    }
