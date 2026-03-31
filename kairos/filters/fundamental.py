"""Fundamental filters: PE, ROE, debt, earnings growth."""

from __future__ import annotations

from typing import Any

from core.logger import get_logger
from kairos.data.fetcher import extract_fundamental, extract_market_cap_cr

_log = get_logger(__name__)


def passes_market_cap_filter(info: dict[str, Any], min_cr: int = 500) -> bool:
    """Check if market cap exceeds minimum in crores."""
    mcap_cr = extract_market_cap_cr(info)
    return mcap_cr >= min_cr


def passes_pe_filter(info: dict[str, Any], max_pe: float = 100.0) -> bool:
    """Check if P/E ratio is reasonable."""
    pe = extract_fundamental(info, "trailingPE")
    if pe <= 0:
        return True
    return pe <= max_pe


def passes_roe_filter(info: dict[str, Any], min_roe: float = 0.05) -> bool:
    """Check if ROE meets minimum threshold."""
    roe = extract_fundamental(info, "returnOnEquity")
    return roe >= min_roe


def passes_debt_filter(info: dict[str, Any], max_de: float = 200.0) -> bool:
    """Check if debt-to-equity is within acceptable range."""
    de = extract_fundamental(info, "debtToEquity")
    if de == 0:
        return True
    return de <= max_de


def passes_earnings_growth_filter(info: dict[str, Any], min_growth: float = -0.10) -> bool:
    """Check earnings aren't in severe decline."""
    growth = extract_fundamental(info, "earningsGrowth")
    return growth >= min_growth


def apply_fundamental_filters(
    info: dict[str, Any],
    min_market_cap_cr: int = 500,
) -> bool:
    """Apply all fundamental filters and return pass/fail."""
    checks = [
        passes_market_cap_filter(info, min_market_cap_cr),
        passes_pe_filter(info),
        passes_debt_filter(info),
    ]
    return all(checks)
