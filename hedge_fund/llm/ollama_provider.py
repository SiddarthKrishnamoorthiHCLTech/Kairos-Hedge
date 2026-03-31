"""Ollama local LLM provider implementation."""

from __future__ import annotations

import aiohttp

from core.exceptions import LLMError
from core.logger import get_logger
from hedge_fund.llm.base_provider import BaseLLMProvider

_log = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider for offline operation."""

    def __init__(self, base_url: str, model: str, max_tokens: int, temperature: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call local Ollama API and return generated text."""
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "num_predict": self._max_tokens,
                "temperature": self._temperature,
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise LLMError(f"Ollama HTTP {resp.status}: {body[:200]}", provider="ollama")
                data = await resp.json()
                return data.get("message", {}).get("content", "")

    async def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception:
            return False
