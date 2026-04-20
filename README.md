# Codex

Offline-first prototype for a Jyotish (Vedic Astrology) computational engine.

## What's included

- `jyotish_engine/engine.py`: core chart computation pipeline (time normalization, Julian day, sidereal longitudes, whole-sign houses, Vimshottari seed).
- `jyotish_engine/cli.py`: CLI entrypoint for local chart calculation.
- `schemas/`: JSON schemas for request/result payloads.
- `constants/`: starter constants packs (nakshatras, Vimshottari years/order).
- `rules/parashari/`: starter rule-seed YAML for interpretation engine integration.
- `tests/`: unit tests for core helpers and output structure.

## Run

```bash
python -m jyotish_engine.cli sample_request.json
```

Write to file:

```bash
python -m jyotish_engine.cli sample_request.json -o output.json
```

## Test

```bash
python -m unittest discover -s tests
```

## Notes

- This is a deterministic **offline prototype** and intentionally avoids any external APIs.
- Planetary positions in this prototype use simplified mean-motion formulas for scaffolding.
- For production-grade precision, wire the same interface to a full ephemeris backend.
