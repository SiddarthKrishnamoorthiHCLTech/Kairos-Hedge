"""Mark Minervini trend-template scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class MinerviniFramework(BaseFramework):
    """Scores stocks using Minervini's SEPA trend template criteria."""

    @property
    def name(self) -> str:
        return "Minervini"

    @property
    def weight(self) -> float:
        return 0.15

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate Minervini trend template conditions."""
        close = ohlcv["Close"]
        details: dict[str, float] = {}
        total = 0.0

        details["above_sma150"] = self._score_above_sma(close, 150)
        details["above_sma200"] = self._score_above_sma(close, 200)
        details["sma50_above_sma150"] = self._score_sma_order(close, 50, 150)
        details["sma150_above_sma200"] = self._score_sma_order(close, 150, 200)
        details["sma200_trending_up"] = self._score_sma_trend(close, 200)
        details["within_25pct_of_52w_high"] = self._score_near_high(close)
        details["above_30pct_of_52w_low"] = self._score_above_low(close)

        total = sum(details.values()) / len(details) if details else 0.0
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_above_sma(self, close: pd.Series, period: int) -> float:
        """Score whether price is above a given SMA."""
        sma = self._sma(close, period)
        if pd.isna(sma.iloc[-1]):
            return 0.0
        return 100.0 if close.iloc[-1] > sma.iloc[-1] else 0.0

    def _score_sma_order(self, close: pd.Series, fast: int, slow: int) -> float:
        """Score whether fast SMA is above slow SMA."""
        sma_fast = self._sma(close, fast)
        sma_slow = self._sma(close, slow)
        if pd.isna(sma_fast.iloc[-1]) or pd.isna(sma_slow.iloc[-1]):
            return 0.0
        return 100.0 if sma_fast.iloc[-1] > sma_slow.iloc[-1] else 0.0

    def _score_sma_trend(self, close: pd.Series, period: int) -> float:
        """Score whether SMA is trending upward over last 20 days."""
        sma = self._sma(close, period)
        recent = sma.tail(20).dropna()
        if len(recent) < 10:
            return 0.0
        return 100.0 if recent.iloc[-1] > recent.iloc[0] else 0.0

    def _score_near_high(self, close: pd.Series) -> float:
        """Score if price is within 25% of 52-week high."""
        high_52w = close.tail(252).max()
        if high_52w == 0:
            return 0.0
        pct_from_high = ((high_52w - close.iloc[-1]) / high_52w) * 100
        return 100.0 if pct_from_high <= 25 else 0.0

    def _score_above_low(self, close: pd.Series) -> float:
        """Score if price is at least 30% above 52-week low."""
        low_52w = close.tail(252).min()
        if low_52w == 0:
            return 0.0
        pct_above_low = ((close.iloc[-1] - low_52w) / low_52w) * 100
        return 100.0 if pct_above_low >= 30 else 0.0
