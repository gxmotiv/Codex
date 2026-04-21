# Codex

Offline-first prototype for a Jyotish (Vedic Astrology) computational engine.

## What's included

- `jyotish_engine/engine.py`: core chart computation pipeline (time normalization, Julian day, sidereal longitudes, whole-sign houses, Vimshottari seed).
- `jyotish_engine/cli.py`: CLI entrypoint for local chart calculation.
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

### 2) Run with sample input

```bash
python -m jyotish_engine.cli sample_request.json
```

### 3) Save output to a file

```bash
python -m jyotish_engine.cli sample_request.json -o output.json
```

### 4) Run tests

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

## Notes

- This is a deterministic **offline prototype** and intentionally avoids any external APIs.
- Planetary positions in this prototype use simplified mean-motion formulas for scaffolding.
- For production-grade precision, wire the same interface to a full ephemeris backend.
