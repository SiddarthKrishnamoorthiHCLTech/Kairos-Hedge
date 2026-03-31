"""Custom exception hierarchy for KAIROS-HEDGE."""

from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for system errors."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class KairosError(Exception):
    """Base exception for all KAIROS-HEDGE errors."""

    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> None:
        self.severity = severity
        super().__init__(message)


class DataError(KairosError):
    """Raised when data fetching or processing fails."""

    def __init__(self, message: str, ticker: str = "") -> None:
        self.ticker = ticker
        super().__init__(f"[Data] {ticker}: {message}" if ticker else f"[Data] {message}")


class AgentError(KairosError):
    """Raised when an AI agent fails to produce a valid output."""

    def __init__(self, message: str, agent_name: str = "") -> None:
        self.agent_name = agent_name
        super().__init__(f"[Agent:{agent_name}] {message}" if agent_name else f"[Agent] {message}")


class LLMError(KairosError):
    """Raised when all LLM providers fail."""

    def __init__(self, message: str, provider: str = "") -> None:
        self.provider = provider
        super().__init__(f"[LLM:{provider}] {message}" if provider else f"[LLM] {message}")


class ConfigError(KairosError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str) -> None:
        super().__init__(f"[Config] {message}", ErrorSeverity.CRITICAL)


class NotifierError(KairosError):
    """Raised when notification delivery fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"[Notifier] {message}", ErrorSeverity.LOW)
