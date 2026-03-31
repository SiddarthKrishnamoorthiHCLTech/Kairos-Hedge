"""Google Gemini LLM provider implementation."""

from __future__ import annotations

import aiohttp

from core.exceptions import LLMError
from core.logger import get_logger
from hedge_fund.llm.base_provider import BaseLLMProvider

_log = get_logger(__name__)

_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "gemini"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call Gemini API and return generated text."""
        url = f"{_GEMINI_API_URL}/{self._model}:generateContent?key={self._api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {
                "maxOutputTokens": self._max_tokens,
                "temperature": self._temperature,
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise LLMError(f"Gemini HTTP {resp.status}: {body[:200]}", provider="gemini")
                data = await resp.json()
                return self._extract_text(data)

    @staticmethod
    def _extract_text(data: dict) -> str:
        """Extract text from Gemini response structure."""
        candidates = data.get("candidates", [])
        if not candidates:
            raise LLMError("Gemini returned no candidates", provider="gemini")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise LLMError("Gemini returned no content parts", provider="gemini")
        return parts[0].get("text", "")

    async def is_available(self) -> bool:
        """Check if Gemini API key is valid."""
        if not self._api_key or self._api_key.startswith("AIza_your"):
            return False
        try:
            url = f"{_GEMINI_API_URL}?key={self._api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return resp.status == 200
        except Exception:
            return False
