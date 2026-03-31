"""Groq LLM provider implementation."""

from __future__ import annotations

import aiohttp

from core.exceptions import LLMError
from core.logger import get_logger
from hedge_fund.llm.base_provider import BaseLLMProvider

_log = get_logger(__name__)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(BaseLLMProvider):
    """Groq cloud LLM provider using Llama models."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "groq"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API and return generated text."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(_GROQ_API_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise LLMError(f"Groq HTTP {resp.status}: {body[:200]}", provider="groq")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]

    async def is_available(self) -> bool:
        """Check if Groq API key is set and service responds."""
        if not self._api_key or self._api_key.startswith("gsk_your"):
            return False
        try:
            headers = {"Authorization": f"Bearer {self._api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return resp.status == 200
        except Exception:
            return False
