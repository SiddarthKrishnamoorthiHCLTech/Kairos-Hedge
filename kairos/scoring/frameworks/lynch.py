"""Peter Lynch GARP scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class LynchFramework(BaseFramework):
    """Scores stocks using Peter Lynch's growth-at-reasonable-price approach."""

    @property
    def name(self) -> str:
        return "Lynch"

    @property
    def weight(self) -> float:
        return 0.08

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate PEG, earnings growth, and business simplicity."""
        details: dict[str, float] = {}

        details["peg_ratio"] = self._score_peg(info)
        details["earnings_growth"] = self._score_earnings_growth(info)
        details["revenue_growth"] = self._score_revenue_growth(info)
        details["debt_level"] = self._score_debt(info)
        details["insider_ownership"] = self._score_insider(info)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_peg(self, info: dict) -> float:
        """Score PEG ratio (1.0 is fair, below is undervalued)."""
        peg = self._safe_get(info, "pegRatio")
        if peg <= 0:
            return 30.0
        if peg < 0.5:
            return 100.0
        if peg < 1.0:
            return 85.0
        if peg < 1.5:
            return 60.0
        if peg < 2.0:
            return 35.0
        return 10.0

    def _score_earnings_growth(self, info: dict) -> float:
        """Score earnings growth rate."""
        growth = self._safe_get(info, "earningsGrowth")
        if growth > 0.25:
            return 100.0
        if growth > 0.15:
            return 80.0
        if growth > 0.08:
            return 55.0
        if growth > 0:
            return 35.0
        return 10.0

    def _score_revenue_growth(self, info: dict) -> float:
        """Score revenue growth rate."""
        growth = self._safe_get(info, "revenueGrowth")
        if growth > 0.20:
            return 100.0
        if growth > 0.10:
            return 75.0
        if growth > 0.05:
            return 50.0
        return 20.0

    def _score_debt(self, info: dict) -> float:
        """Score debt level (Lynch prefers low debt)."""
        de = self._safe_get(info, "debtToEquity")
        if de == 0:
            return 60.0
        if de < 25:
            return 100.0
        if de < 60:
            return 70.0
        if de < 100:
            return 40.0
        return 15.0

    def _score_insider(self, info: dict) -> float:
        """Score insider/promoter ownership."""
        insider = self._safe_get(info, "heldPercentInsiders")
        if insider > 0.30:
            return 90.0
        if insider > 0.15:
            return 70.0
        if insider > 0.05:
            return 50.0
        return 30.0
