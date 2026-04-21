# Codex

Offline-first prototype for a Jyotish (Vedic Astrology) computational engine.

## What's included

- `jyotish_engine/engine.py`: core chart computation pipeline (time normalization, Julian day, sidereal longitudes, whole-sign houses, Vimshottari seed).
- `jyotish_engine/interpretation.py`: System #1 starter interpretation engine with deterministic traceable scoring.
- `jyotish_engine/cli.py`: CLI entrypoint with `chart` and `interpret` modes.
- `schemas/`: JSON schemas for request/result payloads.
- `constants/`: starter constants packs (nakshatras, Vimshottari years/order).
- `rules/parashari/`: starter rule-seed YAML for interpretation engine integration.
- `tests/`: unit tests for core helpers and output structure.

## Quick start (copy/paste)

### 1) Verify Python

```bash
python --version
```

Use Python 3.10+.

### 2) Compute chart only

```bash
python -m jyotish_engine.cli chart sample_request.json
```

### 3) Compute chart + interpretation (System #1)

```bash
python -m jyotish_engine.cli interpret sample_request.json
```

### 4) Save output to a file

```bash
python -m jyotish_engine.cli interpret sample_request.json -o output.json
```

### 5) Run tests

```bash
python -m unittest discover -s tests
```

## Input format

Example request (`sample_request.json`):

```json
{
  "request_id": "demo-1",
  "datetime_local": "1992-10-14T08:45:00",
  "timezone": "Asia/Kolkata",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "config": {
    "ayanamsha_deg": 24.0,
    "house_system": "whole_sign"
  }
}
```

## Common issues

- `ModuleNotFoundError`: run commands from repo root (`/workspace/Codex`).
- `ZoneInfoNotFoundError`: use a valid IANA timezone (example: `Asia/Kolkata`, `America/New_York`).
- Wrong datetime parsing: use ISO-like format (`YYYY-MM-DDTHH:MM:SS`).
- CLI argument error: provide a command (`chart` or `interpret`) before the input file.

## Notes

- This is a deterministic **offline prototype** and intentionally avoids any external APIs.
- Planetary positions in this prototype use simplified mean-motion formulas for scaffolding.
- Interpretation output is currently heuristic and traceable, designed for extension into full rule-pack execution.
