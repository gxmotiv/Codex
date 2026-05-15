# KP Astrology Workbench

Initial full-stack project structure for a KP astrology calculation and prediction workbench.

## Apps

- `frontend/` — React + Vite + Tailwind CSS interface.
- `backend/` — FastAPI API, SQLAlchemy models, Alembic migrations, local LLM connectors, and KP calculation engine.
- `backend/app/kp_engine/` — Swiss Ephemeris wrappers, KP ayanamsa, Placidus cusps, nakshatra/sub/sub-sub lords, significators, dashas, and prediction JSON.
- `backend/app/llm/` — Ollama and LM Studio HTTP integrations.

## Run locally

```bash
docker compose up --build
```

Enable the bundled Ollama service with:

```bash
docker compose --profile ollama up --build
```

## Backend tests

```bash
cd backend
pytest
```
