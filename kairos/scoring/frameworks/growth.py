"""Growth investing scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class GrowthFramework(BaseFramework):
    """Scores stocks using growth investing metrics."""

    @property
    def name(self) -> str:
        return "Growth"

    @property
    def weight(self) -> float:
        return 0.06

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate growth characteristics."""
        details: dict[str, float] = {}

        details["revenue_growth"] = self._score_revenue(info)
        details["earnings_growth"] = self._score_earnings(info)
        details["operating_margin_trend"] = self._score_margin(info)
        details["roe_growth"] = self._score_roe(info)
        details["price_momentum"] = self._score_price_momentum(ohlcv["Close"])

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_revenue(self, info: dict) -> float:
        """Score revenue growth rate."""
        growth = self._safe_get(info, "revenueGrowth")
        if growth > 0.30:
            return 100.0
        if growth > 0.20:
            return 85.0
        if growth > 0.10:
            return 65.0
        if growth > 0.05:
            return 40.0
        return 10.0

    def _score_earnings(self, info: dict) -> float:
        """Score earnings growth rate."""
        growth = self._safe_get(info, "earningsGrowth")
        if growth > 0.30:
            return 100.0
        if growth > 0.20:
            return 85.0
        if growth > 0.10:
            return 60.0
        if growth > 0:
            return 35.0
        return 10.0

    def _score_margin(self, info: dict) -> float:
        """Score operating margin quality."""
        margin = self._safe_get(info, "operatingMargins")
        if margin > 0.25:
            return 100.0
        if margin > 0.15:
            return 75.0
        if margin > 0.08:
            return 50.0
        return 20.0

    def _score_roe(self, info: dict) -> float:
        """Score return on equity for growth quality."""
        roe = self._safe_get(info, "returnOnEquity")
        if roe > 0.25:
            return 100.0
        if roe > 0.18:
            return 80.0
        if roe > 0.12:
            return 55.0
        return 20.0

    def _score_price_momentum(self, close: pd.Series) -> float:
        """Score 6-month price action for growth stocks."""
        if len(close) < 126:
            return 50.0
        ret = (close.iloc[-1] / close.iloc[-126] - 1) * 100
        if ret > 40:
            return 100.0
        if ret > 20:
            return 80.0
        if ret > 10:
            return 60.0
        if ret > 0:
            return 40.0
        return 10.0
