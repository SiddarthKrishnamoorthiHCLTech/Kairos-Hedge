"""Pydantic v2 data models for all inter-layer communication."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Signal(str, Enum):
    """Trading signal emitted by agents."""

    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class TradingStyle(str, Enum):
    """Supported trading styles."""

    POSITIONAL_SWING = "positional_swing"


class Market(str, Enum):
    """Supported markets."""

    NSE = "NSE"


class AgentOutput(BaseModel):
    """Schema for a single agent's analysis of one stock."""

    agent: str = Field(description="Agent display name")
    signal: Signal = Field(description="BUY / HOLD / SELL")
    confidence: int = Field(ge=0, le=100, description="Confidence 0–100")
    reasoning: str = Field(description="One-paragraph rationale")
    key_risks: list[str] = Field(default_factory=list, description="Top risk factors")


class StockScore(BaseModel):
    """KAIROS scoring result for a single framework."""

    framework: str
    score: float = Field(ge=0, le=100)
    details: dict[str, float] = Field(default_factory=dict)


class ShortlistItem(BaseModel):
    """A single stock on the KAIROS shortlist."""

    ticker: str
    name: str = ""
    sector: str = ""
    kairos_score: float = Field(ge=0, le=100)
    framework_scores: list[StockScore] = Field(default_factory=list)
    market_cap_cr: float = 0.0
    avg_volume: float = 0.0
    current_price: float = 0.0
    rs_rating: float = 0.0


class Shortlist(BaseModel):
    """Complete KAIROS output passed to Hedge Fund."""

    date: date
    items: list[ShortlistItem] = Field(default_factory=list)
    universe_size: int = 0
    filtered_count: int = 0


class StockDecision(BaseModel):
    """Final Hedge Fund decision for a single stock."""

    ticker: str
    consensus: Signal
    consensus_confidence: int = Field(ge=0, le=100)
    entry_zone: str = ""
    stop_loss: str = ""
    target_1: str = ""
    target_2: str = ""
    hold_weeks: str = ""
    agent_votes: dict[str, int] = Field(default_factory=dict)
    disagreements: list[str] = Field(default_factory=list)
    valid_trade: bool = False
    agent_outputs: list[AgentOutput] = Field(default_factory=list)


class WeeklyReport(BaseModel):
    """Full weekly report combining KAIROS + Hedge Fund."""

    date: date
    shortlist: Shortlist
    decisions: list[StockDecision] = Field(default_factory=list)
    valid_trades: int = 0
    total_screened: int = 0
    skip_week: bool = False
    skip_message: str = ""
