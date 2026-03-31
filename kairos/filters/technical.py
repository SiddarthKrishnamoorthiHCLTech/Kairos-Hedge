"""Technical filters: Stage 2, RS, breakout, volume."""

from __future__ import annotations

import pandas as pd

from core.logger import get_logger

_log = get_logger(__name__)


def passes_stage2_filter(ohlcv: pd.DataFrame) -> bool:
    """Check if stock is in Weinstein Stage 2 uptrend."""
    close = ohlcv["Close"]
    if len(close) < 200:
        return False
    sma50 = close.rolling(50).mean().iloc[-1]
    sma150 = close.rolling(150).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1]
    price = close.iloc[-1]
    if pd.isna(sma50) or pd.isna(sma150) or pd.isna(sma200):
        return False
    return price > sma50 > sma150 > sma200


def passes_rs_filter(ohlcv: pd.DataFrame, min_rs: float = 0.0) -> bool:
    """Check relative strength via 6-month return threshold."""
    close = ohlcv["Close"]
    if len(close) < 126:
        return True
    ret_6m = (close.iloc[-1] / close.iloc[-126] - 1) * 100
    return ret_6m > min_rs


def passes_breakout_filter(ohlcv: pd.DataFrame) -> bool:
    """Check if stock is breaking out of recent consolidation."""
    close = ohlcv["Close"]
    if len(close) < 30:
        return True
    high_20 = close.tail(20).max()
    high_60 = close.tail(60).max() if len(close) >= 60 else high_20
    near_high = close.iloc[-1] >= high_20 * 0.97
    breakout = close.iloc[-1] >= high_60 * 0.95
    return near_high or breakout


def passes_volume_filter(ohlcv: pd.DataFrame, min_avg_volume: int = 100000) -> bool:
    """Check if average volume meets minimum threshold."""
    volume = ohlcv["Volume"]
    avg_vol = volume.tail(20).mean()
    return avg_vol >= min_avg_volume


def compute_rs_rating(ohlcv: pd.DataFrame) -> float:
    """Compute relative strength rating (0–100)."""
    close = ohlcv["Close"]
    if len(close) < 252:
        return 50.0
    ret_3m = (close.iloc[-1] / close.iloc[-63] - 1) if len(close) >= 63 else 0.0
    ret_6m = (close.iloc[-1] / close.iloc[-126] - 1) if len(close) >= 126 else 0.0
    ret_12m = (close.iloc[-1] / close.iloc[-252] - 1) if len(close) >= 252 else 0.0
    composite = (ret_3m * 0.4 + ret_6m * 0.35 + ret_12m * 0.25) * 100
    return max(0.0, min(100.0, 50.0 + composite))


def apply_technical_filters(
    ohlcv: pd.DataFrame,
    min_avg_volume: int = 100000,
) -> tuple[bool, float]:
    """Apply all technical filters and return (passed, rs_rating)."""
    rs = compute_rs_rating(ohlcv)
    passed = all([
        passes_stage2_filter(ohlcv),
        passes_rs_filter(ohlcv),
        passes_volume_filter(ohlcv, min_avg_volume),
    ])
    return passed, rs
