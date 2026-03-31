"""Abstract base class for all LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Interface every LLM provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send a prompt and return the text response."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this provider is currently reachable."""
