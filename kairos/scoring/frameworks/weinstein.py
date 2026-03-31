"""Stan Weinstein stage analysis scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class WeinsteinFramework(BaseFramework):
    """Scores stocks using Weinstein's four-stage analysis."""

    @property
    def name(self) -> str:
        return "Weinstein"

    @property
    def weight(self) -> float:
        return 0.12

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate Weinstein stage 2 characteristics."""
        close = ohlcv["Close"]
        volume = ohlcv["Volume"]
        details: dict[str, float] = {}

        details["stage_2_trend"] = self._score_stage2(close)
        details["sma30_slope"] = self._score_sma30_slope(close)
        details["volume_confirmation"] = self._score_volume_confirm(close, volume)
        details["rs_line"] = self._score_rs_line(close)
        details["price_above_sma30"] = self._score_above_sma30(close)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_stage2(self, close: pd.Series) -> float:
        """Score whether stock is in stage 2 (advancing)."""
        sma30 = self._sma(close, 30)
        sma_slope = sma30.tail(20).dropna()
        if len(sma_slope) < 10:
            return 40.0
        above_sma = close.iloc[-1] > sma30.iloc[-1] if not pd.isna(sma30.iloc[-1]) else False
        rising = sma_slope.iloc[-1] > sma_slope.iloc[0]
        if above_sma and rising:
            return 100.0
        if above_sma:
            return 60.0
        return 20.0

    def _score_sma30_slope(self, close: pd.Series) -> float:
        """Score the slope of 30-week (150-day) moving average."""
        sma150 = self._sma(close, 150)
        recent = sma150.tail(20).dropna()
        if len(recent) < 10:
            return 50.0
        slope = (recent.iloc[-1] - recent.iloc[0]) / recent.iloc[0] * 100
        if slope > 5:
            return 100.0
        if slope > 2:
            return 75.0
        if slope > 0:
            return 50.0
        return 15.0

    def _score_volume_confirm(self, close: pd.Series, volume: pd.Series) -> float:
        """Score volume confirmation of uptrend."""
        if len(close) < 30:
            return 50.0
        up_days = close.diff().tail(20) > 0
        avg_up_vol = volume.tail(20)[up_days].mean()
        avg_down_vol = volume.tail(20)[~up_days].mean()
        if pd.isna(avg_up_vol) or pd.isna(avg_down_vol) or avg_down_vol == 0:
            return 50.0
        ratio = avg_up_vol / avg_down_vol
        if ratio > 1.5:
            return 100.0
        if ratio > 1.0:
            return 65.0
        return 25.0

    def _score_rs_line(self, close: pd.Series) -> float:
        """Score relative strength via 3-month performance."""
        if len(close) < 63:
            return 50.0
        ret_3m = (close.iloc[-1] / close.iloc[-63] - 1) * 100
        if ret_3m > 20:
            return 100.0
        if ret_3m > 10:
            return 75.0
        if ret_3m > 0:
            return 50.0
        return 15.0

    def _score_above_sma30(self, close: pd.Series) -> float:
        """Score current price relative to 30-day SMA."""
        pct = self._pct_above_sma(close, 30)
        if pct > 10:
            return 90.0
        if pct > 3:
            return 75.0
        if pct > 0:
            return 55.0
        return 20.0
