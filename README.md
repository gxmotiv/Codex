# Codex

Offline-first prototype for a Jyotish (Vedic Astrology) computational + interpretation stack.

## What's included

- `jyotish_engine/engine.py`: Engine #1 mathematical layer (UTC/JD conversion, sidereal longitudes, node mode, whole-sign houses, D7/D9/D10 vargas, Vimshottari seed).
- `jyotish_engine/interpretation.py`: System #1 intelligence layer (knowledge base, synthesis, dignity, yoga detection, varga validation, dasha×transit signal, remedial suggestions).
- `jyotish_engine/cli.py`: CLI entrypoint with `chart` and `interpret` modes.
- `schemas/`: JSON schemas for request/result payloads.
- `constants/`: starter constants packs.
- `rules/parashari/`: starter rule-seed YAML.
- `tests/`: unit tests.

## Quick start

```bash
python --version
python -m jyotish_engine.cli chart sample_request.json
python -m jyotish_engine.cli interpret sample_request.json
python -m unittest discover -s tests
```

Save output to file:

```bash
python -m jyotish_engine.cli interpret sample_request.json -o output.json
```

## Input format

`sample_request.json`:

```json
{
  "request_id": "demo-1",
  "datetime_local": "1992-10-14T08:45:00",
  "timezone": "Asia/Kolkata",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "config": {
    "ayanamsha_deg": 24.0,
    "house_system": "whole_sign",
    "node_mode": "true"
  }
}
```

## Notes

- Fully offline prototype; no external API calls.
- Astronomy is scaffold-level mean-motion math for deterministic development.
- System #1 is a structured rule scaffold aligned to: knowledge base -> synthesis -> yoga -> varga check -> predictive timing -> remedies.
