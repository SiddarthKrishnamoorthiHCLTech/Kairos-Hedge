"""Quality factor scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class QualityFramework(BaseFramework):
    """Scores stocks using quality factor metrics."""

    @property
    def name(self) -> str:
        return "Quality"

    @property
    def weight(self) -> float:
        return 0.06

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate business quality metrics."""
        details: dict[str, float] = {}

        details["roe_quality"] = self._score_roe(info)
        details["roa_quality"] = self._score_roa(info)
        details["gross_margin"] = self._score_gross_margin(info)
        details["debt_quality"] = self._score_debt(info)
        details["earnings_stability"] = self._score_stability(ohlcv["Close"])

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_roe(self, info: dict) -> float:
        """Score ROE as quality indicator."""
        roe = self._safe_get(info, "returnOnEquity")
        if roe > 0.25:
            return 100.0
        if roe > 0.18:
            return 80.0
        if roe > 0.12:
            return 55.0
        if roe > 0.05:
            return 30.0
        return 10.0

    def _score_roa(self, info: dict) -> float:
        """Score return on assets."""
        roa = self._safe_get(info, "returnOnAssets")
        if roa > 0.15:
            return 100.0
        if roa > 0.10:
            return 80.0
        if roa > 0.05:
            return 55.0
        return 20.0

    def _score_gross_margin(self, info: dict) -> float:
        """Score gross margins as moat indicator."""
        gm = self._safe_get(info, "grossMargins")
        if gm > 0.50:
            return 100.0
        if gm > 0.35:
            return 80.0
        if gm > 0.20:
            return 55.0
        return 20.0

    def _score_debt(self, info: dict) -> float:
        """Score balance sheet quality."""
        de = self._safe_get(info, "debtToEquity")
        if de == 0:
            return 60.0
        if de < 20:
            return 100.0
        if de < 50:
            return 75.0
        if de < 100:
            return 45.0
        return 15.0

    def _score_stability(self, close: pd.Series) -> float:
        """Score price stability as quality proxy."""
        if len(close) < 60:
            return 50.0
        returns = close.pct_change().dropna().tail(60)
        vol = returns.std() * (252 ** 0.5)
        if vol < 0.20:
            return 100.0
        if vol < 0.30:
            return 75.0
        if vol < 0.45:
            return 50.0
        return 20.0
