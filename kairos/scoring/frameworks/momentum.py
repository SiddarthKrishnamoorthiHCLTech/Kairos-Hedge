"""Momentum scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class MomentumFramework(BaseFramework):
    """Scores stocks using multi-timeframe momentum signals."""

    @property
    def name(self) -> str:
        return "Momentum"

    @property
    def weight(self) -> float:
        return 0.10

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate momentum across multiple timeframes."""
        close = ohlcv["Close"]
        volume = ohlcv["Volume"]
        details: dict[str, float] = {}

        details["return_1m"] = self._score_return(close, 21)
        details["return_3m"] = self._score_return(close, 63)
        details["return_6m"] = self._score_return(close, 126)
        details["rsi_momentum"] = self._score_rsi_momentum(close)
        details["volume_momentum"] = self._score_vol_momentum(volume)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_return(self, close: pd.Series, days: int) -> float:
        """Score price return over given period."""
        if len(close) < days:
            return 50.0
        ret = (close.iloc[-1] / close.iloc[-days] - 1) * 100
        if ret > 25:
            return 100.0
        if ret > 15:
            return 85.0
        if ret > 8:
            return 70.0
        if ret > 0:
            return 50.0
        if ret > -10:
            return 25.0
        return 5.0

    def _score_rsi_momentum(self, close: pd.Series) -> float:
        """Score RSI for constructive momentum (50–70 ideal)."""
        rsi = self._rsi(close)
        if 55 <= rsi <= 70:
            return 100.0
        if 50 <= rsi <= 75:
            return 80.0
        if 40 <= rsi <= 80:
            return 55.0
        if rsi > 80:
            return 30.0
        return 15.0

    def _score_vol_momentum(self, volume: pd.Series) -> float:
        """Score volume trend (expanding volume preferred)."""
        if len(volume) < 50:
            return 50.0
        avg_10 = volume.tail(10).mean()
        avg_50 = volume.tail(50).mean()
        if avg_50 == 0:
            return 50.0
        ratio = avg_10 / avg_50
        if ratio > 1.5:
            return 100.0
        if ratio > 1.2:
            return 75.0
        if ratio > 0.9:
            return 50.0
        return 20.0
