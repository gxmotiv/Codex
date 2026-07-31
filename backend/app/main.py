from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import SavedChart, SessionLocal, init_db
from .kp_engine.chart import ChartRequest, build_chart
from .kp_engine.predictions import MODULE_RULES, evaluate_module
from .kp_engine.golden import load_golden_dataset
from .kp_engine.sub_lords import division_info, kp_subdivision_table
from .llm.local import call_local_llm, validate_interpretation
from .llm.rag import retrieve_rules

app = FastAPI(title="Local KP Astrology AI", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class PredictionRequest(BaseModel):
    chart: ChartRequest
    module: str = "marriage"
    question: str = ""
    llm_provider: Literal["ollama", "lmstudio"] = "ollama"
    llm_model: str = "llama3"
    use_llm: bool = True


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-only"}


@app.post("/api/chart")
def chart(req: ChartRequest) -> dict[str, Any]:
    result = build_chart(req)
    with SessionLocal() as db:
        db.add(SavedChart(name=req.name, payload=result))
        db.commit()
    return result


@app.get("/api/golden")
def golden() -> dict[str, Any]:
    rows = load_golden_dataset()
    return {"count": len(rows), "rows": rows}


@app.get("/api/subdivisions")
def subdivisions() -> dict[str, Any]:
    rows = kp_subdivision_table()
    return {"count": len(rows), "rows": rows}


@app.get("/api/degree/{longitude}")
def degree_lookup(longitude: float) -> dict[str, Any]:
    return division_info(longitude).__dict__


@app.post("/api/predict")
async def predict(req: PredictionRequest) -> dict[str, Any]:
    if req.module not in MODULE_RULES:
        req.module = "marriage"
    chart_payload = build_chart(req.chart)
    structured = evaluate_module(req.module, chart_payload, req.question)
    structured["retrieved_rules"] = retrieve_rules(req.question, req.module)
    response: dict[str, Any] = {"structured": structured, "llm": {"available": False, "text": None}, "validator": None}
    if req.use_llm:
        llm = await call_local_llm(structured, req.llm_model, req.llm_provider)
        response["llm"] = llm
        if llm.get("available") and llm.get("text"):
            verdict = await validate_interpretation(structured, llm["text"], req.llm_model, req.llm_provider)
            response["validator"] = verdict
            if verdict.get("status") != "VALID":
                response["llm"]["warning"] = "Validator did not approve the interpretation; rely on structured JSON."
    return response
