"""Value investing scoring framework."""

from __future__ import annotations

import pandas as pd

from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework


class ValueFramework(BaseFramework):
    """Scores stocks using multi-factor value investing metrics."""

    @property
    def name(self) -> str:
        return "Value"

    @property
    def weight(self) -> float:
        return 0.06

    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Evaluate composite value metrics."""
        details: dict[str, float] = {}

        details["pe_value"] = self._score_pe(info)
        details["pb_value"] = self._score_pb(info)
        details["ev_ebitda"] = self._score_ev_ebitda(info)
        details["fcf_yield"] = self._score_fcf_yield(info)
        details["dividend"] = self._score_dividend(info)

        total = sum(details.values()) / len(details)
        return StockScore(framework=self.name, score=self._clamp(total), details=details)

    def _score_pe(self, info: dict) -> float:
        """Score trailing P/E ratio."""
        pe = self._safe_get(info, "trailingPE")
        if pe <= 0:
            return 20.0
        if pe < 12:
            return 100.0
        if pe < 18:
            return 75.0
        if pe < 30:
            return 45.0
        return 10.0

    def _score_pb(self, info: dict) -> float:
        """Score price-to-book ratio."""
        pb = self._safe_get(info, "priceToBook")
        if pb <= 0:
            return 20.0
        if pb < 1.5:
            return 100.0
        if pb < 3.0:
            return 65.0
        if pb < 5.0:
            return 35.0
        return 10.0

    def _score_ev_ebitda(self, info: dict) -> float:
        """Score EV/EBITDA ratio."""
        ev_ebitda = self._safe_get(info, "enterpriseToEbitda")
        if ev_ebitda <= 0:
            return 30.0
        if ev_ebitda < 8:
            return 100.0
        if ev_ebitda < 12:
            return 75.0
        if ev_ebitda < 20:
            return 45.0
        return 10.0

    def _score_fcf_yield(self, info: dict) -> float:
        """Score free cash flow yield."""
        fcf = self._safe_get(info, "freeCashflow")
        mcap = self._safe_get(info, "marketCap")
        if mcap <= 0 or fcf <= 0:
            return 25.0
        fcf_yield = (fcf / mcap) * 100
        if fcf_yield > 8:
            return 100.0
        if fcf_yield > 5:
            return 80.0
        if fcf_yield > 2:
            return 55.0
        return 20.0

    def _score_dividend(self, info: dict) -> float:
        """Score dividend yield for value investors."""
        div = self._safe_get(info, "dividendYield")
        if div > 0.05:
            return 100.0
        if div > 0.03:
            return 75.0
        if div > 0.01:
            return 50.0
        return 25.0
