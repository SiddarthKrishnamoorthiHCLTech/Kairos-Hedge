"""William O'Neil CAN SLIM scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class ONeilFramework(BaseFramework):
    """Scores stocks using O'Neil's CAN SLIM methodology."""

    @property
    def name(self) -> str:
        return "ONeil"

    @property
    def weight(self) -> float:
        return 0.12

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate CAN SLIM criteria."""
        close = ohlcv["Close"]
        volume = ohlcv["Volume"]
        details: dict[str, float] = {}

        details["earnings_growth"] = self._score_earnings(info)
        details["annual_earnings"] = self._score_annual_earnings(info)
        details["new_high"] = self._score_new_high(close)
        details["supply_demand"] = self._score_volume(volume)
        details["leader_laggard"] = self._score_rs(close)
        details["institutional"] = self._score_institutional(info)
        details["market_direction"] = self._score_market_trend(close)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_earnings(self, info: dict) -> float:
        """Score quarterly earnings growth."""
        growth = self._safe_get(info, "earningsQuarterlyGrowth")
        if growth > 0.25:
            return 100.0
        if growth > 0.10:
            return 70.0
        if growth > 0:
            return 40.0
        return 10.0

    def _score_annual_earnings(self, info: dict) -> float:
        """Score annual revenue growth as proxy."""
        growth = self._safe_get(info, "revenueGrowth")
        if growth > 0.20:
            return 100.0
        if growth > 0.10:
            return 70.0
        if growth > 0:
            return 40.0
        return 10.0

    def _score_new_high(self, close: pd.Series) -> float:
        """Score proximity to new 52-week high."""
        high_52w = close.tail(252).max()
        if high_52w == 0:
            return 0.0
        pct_from_high = ((high_52w - close.iloc[-1]) / high_52w) * 100
        if pct_from_high <= 5:
            return 100.0
        if pct_from_high <= 15:
            return 70.0
        if pct_from_high <= 25:
            return 40.0
        return 10.0

    def _score_volume(self, volume: pd.Series) -> float:
        """Score volume expansion (last 10d vs 50d average)."""
        avg_10 = volume.tail(10).mean()
        avg_50 = volume.tail(50).mean()
        if avg_50 == 0:
            return 50.0
        ratio = avg_10 / avg_50
        if ratio > 1.5:
            return 100.0
        if ratio > 1.2:
            return 70.0
        if ratio > 0.8:
            return 50.0
        return 20.0

    def _score_rs(self, close: pd.Series) -> float:
        """Score relative strength via 6-month return."""
        if len(close) < 126:
            return 50.0
        ret_6m = (close.iloc[-1] / close.iloc[-126] - 1) * 100
        if ret_6m > 30:
            return 100.0
        if ret_6m > 15:
            return 75.0
        if ret_6m > 0:
            return 50.0
        return 15.0

    def _score_institutional(self, info: dict) -> float:
        """Score institutional ownership."""
        inst = self._safe_get(info, "heldPercentInstitutions")
        if inst > 0.5:
            return 90.0
        if inst > 0.3:
            return 70.0
        if inst > 0.1:
            return 50.0
        return 30.0

    def _score_market_trend(self, close: pd.Series) -> float:
        """Score overall market trend using SMA200."""
        sma200 = self._sma(close, 200)
        if pd.isna(sma200.iloc[-1]):
            return 50.0
        return 80.0 if close.iloc[-1] > sma200.iloc[-1] else 30.0
