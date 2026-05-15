from __future__ import annotations

from typing import Any

import httpx

SYSTEM_PROMPT = """You are a senior KP Astrologer. Use ONLY the supplied structured chart context and KP rules. Do not invent planets, houses, dashas, or transits. If evidence is mixed or denies the event, say so clearly and cite the cusp sub-lord and house significations that support the conclusion."""
VALIDATOR_PROMPT = """Validate the interpretation against the chart JSON. Check for hallucinated planets/houses, contradictions, and missing cusp sub-lord analysis. Return JSON with status VALID or INVALID and reasons."""


async def call_local_llm(payload: dict[str, Any], model: str = "llama3", provider: str = "ollama") -> dict[str, Any]:
    prompt = f"{SYSTEM_PROMPT}\n\nStructured KP JSON:\n{payload}"
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            if provider == "lmstudio":
                response = await client.post("http://localhost:1234/v1/chat/completions", json={
                    "model": model,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": str(payload)}],
                    "temperature": 0.2,
                })
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]
            else:
                response = await client.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False, "temperature": 0.2})
                response.raise_for_status()
                text = response.json().get("response", "")
    except Exception as exc:
        return {"available": False, "warning": f"Local LLM offline or unreachable: {exc}", "text": None}
    return {"available": True, "text": text}


async def validate_interpretation(context: dict[str, Any], interpretation: str, model: str = "llama3", provider: str = "ollama") -> dict[str, Any]:
    payload = {"context": context, "interpretation": interpretation}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if provider == "lmstudio":
                response = await client.post("http://localhost:1234/v1/chat/completions", json={
                    "model": model,
                    "messages": [{"role": "system", "content": VALIDATOR_PROMPT}, {"role": "user", "content": str(payload)}],
                    "temperature": 0,
                })
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]
            else:
                response = await client.post("http://localhost:11434/api/generate", json={"model": model, "prompt": f"{VALIDATOR_PROMPT}\n{payload}", "stream": False, "temperature": 0})
                response.raise_for_status()
                text = response.json().get("response", "")
    except Exception as exc:
        return {"status": "UNAVAILABLE", "reasons": [str(exc)]}
    return {"status": "VALID" if "VALID" in text.upper() and "INVALID" not in text.upper() else "INVALID", "raw": text}
