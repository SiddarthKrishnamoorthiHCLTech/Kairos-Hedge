"""Wyckoff accumulation/distribution scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class WyckoffFramework(BaseFramework):
    """Scores stocks using Wyckoff accumulation/distribution analysis."""

    @property
    def name(self) -> str:
        return "Wyckoff"

    @property
    def weight(self) -> float:
        return 0.10

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate Wyckoff accumulation signals."""
        close = ohlcv["Close"]
        volume = ohlcv["Volume"]
        high = ohlcv["High"]
        low = ohlcv["Low"]
        details: dict[str, float] = {}

        details["accumulation"] = self._score_accumulation(close, volume)
        details["spring_pattern"] = self._score_spring(close, low)
        details["effort_vs_result"] = self._score_effort_result(close, volume)
        details["sign_of_strength"] = self._score_sos(close, volume, high)
        details["markup_phase"] = self._score_markup(close)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_accumulation(self, close: pd.Series, volume: pd.Series) -> float:
        """Score accumulation via price-volume convergence."""
        if len(close) < 40:
            return 50.0
        price_flat = abs(close.iloc[-1] / close.iloc[-40] - 1) < 0.10
        vol_decline = volume.tail(20).mean() < volume.tail(40).mean() * 0.8
        if price_flat and vol_decline:
            return 90.0
        if price_flat:
            return 60.0
        return 30.0

    def _score_spring(self, close: pd.Series, low: pd.Series) -> float:
        """Score spring pattern (false breakdown followed by recovery)."""
        if len(close) < 60:
            return 50.0
        support = low.tail(60).quantile(0.10)
        recent_low = low.tail(5).min()
        recovered = close.iloc[-1] > support
        dipped = recent_low < support
        if dipped and recovered:
            return 95.0
        if recovered:
            return 55.0
        return 25.0

    def _score_effort_result(self, close: pd.Series, volume: pd.Series) -> float:
        """Score effort vs result (volume vs price movement)."""
        if len(close) < 10:
            return 50.0
        price_change = abs(close.iloc[-1] / close.iloc[-5] - 1)
        vol_avg = volume.tail(5).mean()
        vol_norm = volume.tail(50).mean()
        if vol_norm == 0:
            return 50.0
        vol_ratio = vol_avg / vol_norm
        if price_change > 0.03 and vol_ratio > 1.3:
            return 90.0
        if price_change > 0.02 and vol_ratio > 1.0:
            return 65.0
        return 35.0

    def _score_sos(self, close: pd.Series, volume: pd.Series, high: pd.Series) -> float:
        """Score sign of strength (breakout on volume)."""
        if len(close) < 30:
            return 50.0
        resistance = high.tail(30).quantile(0.90)
        broke_out = close.iloc[-1] > resistance
        vol_spike = volume.iloc[-1] > volume.tail(20).mean() * 1.5
        if broke_out and vol_spike:
            return 100.0
        if broke_out:
            return 70.0
        return 30.0

    def _score_markup(self, close: pd.Series) -> float:
        """Score markup phase characteristics."""
        if len(close) < 50:
            return 50.0
        sma20 = self._sma(close, 20)
        sma50 = self._sma(close, 50)
        if pd.isna(sma20.iloc[-1]) or pd.isna(sma50.iloc[-1]):
            return 50.0
        above_both = close.iloc[-1] > sma20.iloc[-1] > sma50.iloc[-1]
        return 90.0 if above_both else 35.0
