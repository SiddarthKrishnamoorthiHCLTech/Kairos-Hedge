"""Benjamin Graham deep value scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class GrahamFramework(BaseFramework):
    """Scores stocks using Benjamin Graham's deep value criteria."""

    @property
    def name(self) -> str:
        return "Graham"

    @property
    def weight(self) -> float:
        return 0.07

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate Graham's margin of safety criteria."""
        details: dict[str, float] = {}

        details["pe_ratio"] = self._score_pe(info)
        details["pb_ratio"] = self._score_pb(info)
        details["current_ratio"] = self._score_liquidity(info)
        details["dividend_yield"] = self._score_dividend(info)
        details["graham_number"] = self._score_graham_number(info, ohlcv)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_pe(self, info: dict) -> float:
        """Score P/E ratio (lower preferred)."""
        pe = self._safe_get(info, "trailingPE")
        if pe <= 0:
            return 20.0
        if pe < 10:
            return 100.0
        if pe < 15:
            return 80.0
        if pe < 25:
            return 55.0
        return 15.0

    def _score_pb(self, info: dict) -> float:
        """Score price-to-book ratio."""
        pb = self._safe_get(info, "priceToBook")
        if pb <= 0:
            return 20.0
        if pb < 1.0:
            return 100.0
        if pb < 1.5:
            return 80.0
        if pb < 3.0:
            return 50.0
        return 15.0

    def _score_liquidity(self, info: dict) -> float:
        """Score current ratio (above 2 preferred by Graham)."""
        cr = self._safe_get(info, "currentRatio")
        if cr >= 2.0:
            return 100.0
        if cr >= 1.5:
            return 75.0
        if cr >= 1.0:
            return 45.0
        return 10.0

    def _score_dividend(self, info: dict) -> float:
        """Score dividend yield."""
        div = self._safe_get(info, "dividendYield")
        if div > 0.04:
            return 100.0
        if div > 0.02:
            return 70.0
        if div > 0.005:
            return 45.0
        return 20.0

    def _score_graham_number(self, info: dict, ohlcv: pd.DataFrame) -> float:
        """Score based on Graham number vs current price."""
        eps = self._safe_get(info, "trailingEps")
        bvps = self._safe_get(info, "bookValue")
        if eps <= 0 or bvps <= 0:
            return 30.0
        graham_num = (22.5 * eps * bvps) ** 0.5
        price = float(ohlcv["Close"].iloc[-1])
        if price == 0:
            return 30.0
        ratio = graham_num / price
        if ratio > 1.2:
            return 100.0
        if ratio > 1.0:
            return 75.0
        if ratio > 0.8:
            return 50.0
        return 20.0
