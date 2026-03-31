"""Pydantic-settings configuration loader for KAIROS-HEDGE."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


def _load_yaml_config() -> dict[str, Any]:
    """Read config.yaml from project root."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


_YAML: dict[str, Any] = _load_yaml_config()


class LLMProviderConfig(BaseSettings):
    """Settings for a single LLM provider."""

    model: str = ""
    max_tokens: int = 1000
    temperature: float = 0.3
    base_url: str = ""


class LLMSettings(BaseSettings):
    """All LLM-related settings."""

    primary_provider: str = "groq"
    fallback_order: list[str] = Field(default_factory=lambda: ["groq", "gemini", "openrouter", "ollama"])
    groq: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        model=_YAML.get("llm", {}).get("groq", {}).get("model", "llama-3.3-70b-versatile"),
        max_tokens=_YAML.get("llm", {}).get("groq", {}).get("max_tokens", 1000),
        temperature=_YAML.get("llm", {}).get("groq", {}).get("temperature", 0.3),
    ))
    gemini: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        model=_YAML.get("llm", {}).get("gemini", {}).get("model", "gemini-1.5-flash"),
        max_tokens=_YAML.get("llm", {}).get("gemini", {}).get("max_tokens", 1000),
        temperature=_YAML.get("llm", {}).get("gemini", {}).get("temperature", 0.3),
    ))
    openrouter: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        model=_YAML.get("llm", {}).get("openrouter", {}).get("model", "meta-llama/llama-3.3-70b-instruct:free"),
        max_tokens=_YAML.get("llm", {}).get("openrouter", {}).get("max_tokens", 1000),
        temperature=_YAML.get("llm", {}).get("openrouter", {}).get("temperature", 0.3),
    ))
    ollama: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        model=_YAML.get("llm", {}).get("ollama", {}).get("model", "llama3"),
        base_url=_YAML.get("llm", {}).get("ollama", {}).get("base_url", "http://localhost:11434"),
        max_tokens=_YAML.get("llm", {}).get("ollama", {}).get("max_tokens", 1000),
        temperature=_YAML.get("llm", {}).get("ollama", {}).get("temperature", 0.3),
    ))
    concurrency_limit: int = 3
    retry_attempts: int = 3
    retry_delay_seconds: int = 5


class KairosSettings(BaseSettings):
    """KAIROS screener settings."""

    nse_universe_size: int = 500
    min_kairos_score: int = 65
    top_n_shortlist: int = 10
    min_market_cap_cr: int = 500
    min_avg_volume: int = 100000
    lookback_days: int = 365


class HedgeFundSettings(BaseSettings):
    """Hedge Fund agent settings."""

    min_consensus_confidence: int = 70
    min_buy_agents: int = 10
    sl_percent: float = 5.0
    target_1_percent: float = 10.0
    target_2_percent: float = 18.0
    hold_weeks_min: int = 1
    hold_weeks_max: int = 4


class OutputSettings(BaseSettings):
    """Output and reporting settings."""

    save_json: bool = True
    save_html_report: bool = True
    send_telegram: bool = True
    sync_google_sheets: bool = True
    output_dir: str = "output/"
    archive_dir: str = "output/reports/"


class TradingSettings(BaseSettings):
    """Trading style settings."""

    style: str = "positional_swing"
    market: str = "NSE"
    currency: str = "INR"
    skip_week_message: str = "No valid trade setups this week. Stand aside. ✋"


class AppSettings(BaseSettings):
    """Root application settings combining .env secrets and config.yaml."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    groq_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    google_sheets_credentials_path: str = "credentials/google_service_account.json"
    google_sheet_id: str = ""

    llm: LLMSettings = Field(default_factory=lambda: _build_llm_settings())
    kairos: KairosSettings = Field(default_factory=lambda: _build_kairos_settings())
    hedge_fund: HedgeFundSettings = Field(default_factory=lambda: _build_hedge_fund_settings())
    output: OutputSettings = Field(default_factory=lambda: _build_output_settings())
    trading: TradingSettings = Field(default_factory=lambda: _build_trading_settings())


def _build_llm_settings() -> LLMSettings:
    """Construct LLM settings from YAML."""
    llm_cfg = _YAML.get("llm", {})
    return LLMSettings(
        primary_provider=llm_cfg.get("primary_provider", "groq"),
        fallback_order=llm_cfg.get("fallback_order", ["groq", "gemini", "openrouter", "ollama"]),
        concurrency_limit=llm_cfg.get("concurrency_limit", 3),
        retry_attempts=llm_cfg.get("retry_attempts", 3),
        retry_delay_seconds=llm_cfg.get("retry_delay_seconds", 5),
    )


def _build_kairos_settings() -> KairosSettings:
    """Construct KAIROS settings from YAML."""
    k_cfg = _YAML.get("kairos", {})
    return KairosSettings(**{k: v for k, v in k_cfg.items() if v is not None})


def _build_hedge_fund_settings() -> HedgeFundSettings:
    """Construct Hedge Fund settings from YAML."""
    h_cfg = _YAML.get("hedge_fund", {})
    return HedgeFundSettings(**{k: v for k, v in h_cfg.items() if v is not None})


def _build_output_settings() -> OutputSettings:
    """Construct output settings from YAML."""
    o_cfg = _YAML.get("output", {})
    return OutputSettings(**{k: v for k, v in o_cfg.items() if v is not None})


def _build_trading_settings() -> TradingSettings:
    """Construct trading settings from YAML."""
    t_cfg = _YAML.get("trading", {})
    return TradingSettings(**{k: v for k, v in t_cfg.items() if v is not None})


def load_settings() -> AppSettings:
    """Load and return validated application settings."""
    return AppSettings()
