from dataclasses import dataclass
from typing import Literal

import httpx

from app.config import settings

Provider = Literal["ollama", "lm_studio"]


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    model: str = "llama3.1"
    temperature: float = 0.2


class LocalLLMClient:
    def __init__(self, ollama_url: str = settings.ollama_url, lm_studio_url: str = settings.lm_studio_url):
        self.ollama_url = ollama_url
        self.lm_studio_url = lm_studio_url

    async def generate(self, provider: Provider, request: LLMRequest) -> str:
        if provider == "ollama":
            return await self._ollama(request)
        if provider == "lm_studio":
            return await self._lm_studio(request)
        raise ValueError(f"Unsupported provider: {provider}")

    async def _ollama(self, request: LLMRequest) -> str:
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(self.ollama_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def _lm_studio(self, request: LLMRequest) -> str:
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(self.lm_studio_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
