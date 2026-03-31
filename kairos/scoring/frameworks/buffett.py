"""Warren Buffett value investing scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class BuffettFramework(BaseFramework):
    """Scores stocks using Buffett's value investing principles."""

    @property
    def name(self) -> str:
        return "Buffett"

    @property
    def weight(self) -> float:
        return 0.08

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate Buffett-style fundamentals."""
        details: dict[str, float] = {}

        details["roe"] = self._score_roe(info)
        details["debt_equity"] = self._score_debt(info)
        details["profit_margin"] = self._score_margin(info)
        details["moat_proxy"] = self._score_moat(info)
        details["earnings_consistency"] = self._score_earnings(info)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_roe(self, info: dict) -> float:
        """Score return on equity."""
        roe = self._safe_get(info, "returnOnEquity")
        if roe > 0.20:
            return 100.0
        if roe > 0.15:
            return 80.0
        if roe > 0.10:
            return 55.0
        return 20.0

    def _score_debt(self, info: dict) -> float:
        """Score debt-to-equity ratio (lower is better)."""
        de = self._safe_get(info, "debtToEquity")
        if de == 0:
            return 60.0
        if de < 30:
            return 100.0
        if de < 80:
            return 70.0
        if de < 150:
            return 40.0
        return 10.0

    def _score_margin(self, info: dict) -> float:
        """Score profit margins."""
        margin = self._safe_get(info, "profitMargins")
        if margin > 0.20:
            return 100.0
        if margin > 0.12:
            return 75.0
        if margin > 0.05:
            return 50.0
        return 15.0

    def _score_moat(self, info: dict) -> float:
        """Score competitive moat proxy (gross margins + market cap)."""
        gm = self._safe_get(info, "grossMargins")
        mcap = self._safe_get(info, "marketCap")
        moat_score = 0.0
        if gm > 0.40:
            moat_score += 50.0
        elif gm > 0.25:
            moat_score += 30.0
        else:
            moat_score += 10.0
        if mcap > 1e12:
            moat_score += 50.0
        elif mcap > 1e11:
            moat_score += 35.0
        else:
            moat_score += 15.0
        return moat_score

    def _score_earnings(self, info: dict) -> float:
        """Score earnings growth consistency."""
        growth = self._safe_get(info, "earningsGrowth")
        if growth > 0.15:
            return 90.0
        if growth > 0.08:
            return 65.0
        if growth > 0:
            return 40.0
        return 15.0
