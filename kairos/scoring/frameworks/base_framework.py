"""Abstract base class for all KAIROS scoring frameworks."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from core.schemas import StockScore


class BaseFramework(ABC):
    """Base class every scoring framework must inherit from."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable framework name."""

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight in consensus scoring (0.0–1.0)."""

    @abstractmethod
    def score(self, ohlcv: pd.DataFrame, info: dict) -> StockScore:
        """Score a stock and return structured result."""

    def _sma(self, series: pd.Series, period: int) -> pd.Series:
        """Compute simple moving average."""
        return series.rolling(window=period, min_periods=period).mean()

    def _ema(self, series: pd.Series, period: int) -> pd.Series:
        """Compute exponential moving average."""
        return series.ewm(span=period, adjust=False).mean()

    def _rsi(self, series: pd.Series, period: int = 14) -> float:
        """Compute latest RSI value."""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
        last_gain = gain.iloc[-1] if len(gain) > 0 else 0.0
        last_loss = loss.iloc[-1] if len(loss) > 0 else 1.0
        if last_loss == 0:
            return 100.0
        rs = last_gain / last_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def _atr(self, ohlcv: pd.DataFrame, period: int = 14) -> float:
        """Compute latest Average True Range."""
        high = ohlcv["High"]
        low = ohlcv["Low"]
        close = ohlcv["Close"].shift(1)
        tr = pd.concat([high - low, (high - close).abs(), (low - close).abs()], axis=1).max(axis=1)
        atr_series = tr.rolling(window=period).mean()
        return float(atr_series.iloc[-1]) if len(atr_series) > 0 else 0.0

    def _pct_above_sma(self, close: pd.Series, period: int) -> float:
        """Return how far current price is above SMA as percentage."""
        sma = self._sma(close, period)
        if sma.iloc[-1] == 0 or pd.isna(sma.iloc[-1]):
            return 0.0
        return ((close.iloc[-1] - sma.iloc[-1]) / sma.iloc[-1]) * 100

    def _safe_get(self, info: dict, key: str, default: float = 0.0) -> float:
        """Safely extract a numeric value from info dict."""
        val = info.get(key)
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
        """Clamp a value between low and high."""
        return max(low, min(high, value))
