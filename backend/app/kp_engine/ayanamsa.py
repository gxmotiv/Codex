from app.kp_engine.constants import ZODIAC_DEGREES

KP_AYANAMSA_2000 = 23.85675
ANNUAL_PRECESSION_DEGREES = 50.290966 / 3600.0


def normalize_degrees(value: float) -> float:
    return value % ZODIAC_DEGREES


def kp_ayanamsa(decimal_year: float) -> float:
    """Approximate KP/Newcomb ayanamsa for deterministic validation and tests."""
    return normalize_degrees(KP_AYANAMSA_2000 + (decimal_year - 2000.0) * ANNUAL_PRECESSION_DEGREES)


def tropical_to_sidereal(longitude: float, decimal_year: float) -> float:
    return normalize_degrees(longitude - kp_ayanamsa(decimal_year))
