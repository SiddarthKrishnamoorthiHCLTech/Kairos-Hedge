"""LLM router with automatic failover across providers."""

from __future__ import annotations

import asyncio

from core.config import AppSettings
from core.exceptions import LLMError
from core.logger import get_logger
from hedge_fund.llm.base_provider import BaseLLMProvider
from hedge_fund.llm.gemini_provider import GeminiProvider
from hedge_fund.llm.groq_provider import GroqProvider
from hedge_fund.llm.ollama_provider import OllamaProvider
from hedge_fund.llm.openrouter_provider import OpenRouterProvider

_log = get_logger(__name__)


class LLMRouter:
    """Routes LLM calls with automatic failover across providers."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._providers = self._build_providers()
        self._semaphore = asyncio.Semaphore(settings.llm.concurrency_limit)
        self._active_provider: str = ""

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompt to first available provider with failover."""
        async with self._semaphore:
            return await self._try_providers(system_prompt, user_prompt)

    async def _try_providers(self, system_prompt: str, user_prompt: str) -> str:
        """Attempt each provider in failover order."""
        errors: list[str] = []
        for provider in self._providers:
            for attempt in range(self._settings.llm.retry_attempts):
                try:
                    result = await provider.generate(system_prompt, user_prompt)
                    self._active_provider = provider.name
                    return result
                except LLMError as exc:
                    errors.append(f"{provider.name}(attempt {attempt + 1}): {exc}")
                    _log.warning(f"LLM {provider.name} attempt {attempt + 1} failed: {exc}")
                    await asyncio.sleep(self._settings.llm.retry_delay_seconds)
                except Exception as exc:
                    errors.append(f"{provider.name}: unexpected {exc}")
                    _log.warning(f"LLM {provider.name} unexpected error: {exc}")
                    break
        raise LLMError(f"All providers failed: {'; '.join(errors[-4:])}")

    def _build_providers(self) -> list[BaseLLMProvider]:
        """Build ordered list of LLM providers from config."""
        builder_map = {
            "groq": self._build_groq,
            "gemini": self._build_gemini,
            "openrouter": self._build_openrouter,
            "ollama": self._build_ollama,
        }
        providers: list[BaseLLMProvider] = []
        for name in self._settings.llm.fallback_order:
            builder = builder_map.get(name)
            if builder:
                providers.append(builder())
        return providers

    def _build_groq(self) -> BaseLLMProvider:
        """Build Groq provider."""
        cfg = self._settings.llm.groq
        return GroqProvider(
            api_key=self._settings.groq_api_key,
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

    def _build_gemini(self) -> BaseLLMProvider:
        """Build Gemini provider."""
        cfg = self._settings.llm.gemini
        return GeminiProvider(
            api_key=self._settings.gemini_api_key,
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

    def _build_openrouter(self) -> BaseLLMProvider:
        """Build OpenRouter provider."""
        cfg = self._settings.llm.openrouter
        return OpenRouterProvider(
            api_key=self._settings.openrouter_api_key,
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

    def _build_ollama(self) -> BaseLLMProvider:
        """Build Ollama provider."""
        cfg = self._settings.llm.ollama
        return OllamaProvider(
            base_url=cfg.base_url or self._settings.ollama_base_url,
            model=cfg.model or self._settings.ollama_model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )
