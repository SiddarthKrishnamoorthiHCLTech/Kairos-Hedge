"""yfinance data fetcher for NSE OHLCV and fundamentals."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from curl_cffi.requests import Session as CurlSession
import pandas as pd
import yfinance as yf

from core.exceptions import DataError
from core.logger import get_logger

_log = get_logger(__name__)

# Corporate SSL proxies inject their own CA cert which curl_cffi doesn't trust.
# Creating a shared session with verify=False bypasses this safely for data fetching.
_shared_session = CurlSession(impersonate="chrome", verify=False)


@dataclass(slots=True)
class StockData:
    """Container for a single stock's fetched data."""

    ticker: str
    ohlcv: pd.DataFrame = field(default_factory=pd.DataFrame)
    info: dict[str, Any] = field(default_factory=dict)
    valid: bool = False


@dataclass(slots=True)
class DataFetcher:
    """Fetches OHLCV and fundamental data from yfinance for NSE stocks."""

    lookback_days: int = 365

    async def fetch(self, ticker: str) -> StockData:
        """Fetch all data for a single NSE ticker."""
        nse_ticker = self._to_nse_symbol(ticker)
        try:
            return await asyncio.to_thread(self._sync_fetch, ticker, nse_ticker)
        except Exception as exc:
            _log.debug(f"Fetch failed for {ticker}: {exc}")
            return StockData(ticker=ticker)

    async def fetch_batch(self, tickers: list[str]) -> list[StockData]:
        """Fetch data for multiple tickers concurrently."""
        tasks = [self.fetch(t) for t in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid: list[StockData] = []
        for result in results:
            if isinstance(result, Exception):
                _log.warning(f"Batch fetch error: {result}")
                continue
            if isinstance(result, StockData):
                valid.append(result)
        return valid

    def _sync_fetch(self, ticker: str, nse_ticker: str) -> StockData:
        """Synchronous yfinance fetch executed in thread pool."""
        yf_obj = yf.Ticker(nse_ticker, session=_shared_session)
        ohlcv = yf_obj.history(period=f"{self.lookback_days}d")
        if ohlcv.empty:
            raise DataError("No OHLCV data returned", ticker=ticker)
        info = self._safe_info(yf_obj)
        return StockData(
            ticker=ticker,
            ohlcv=ohlcv,
            info=info,
            valid=len(ohlcv) >= 50,
        )

    @staticmethod
    def _safe_info(yf_obj: yf.Ticker) -> dict[str, Any]:
        """Extract info dict with fallback on failure."""
        try:
            return dict(yf_obj.info) if yf_obj.info else {}
        except Exception:
            return {}

    @staticmethod
    def _to_nse_symbol(ticker: str) -> str:
        """Append .NS suffix for yfinance NSE lookup."""
        cleaned = ticker.strip().upper()
        if not cleaned.endswith(".NS"):
            return f"{cleaned}.NS"
        return cleaned


def extract_fundamental(info: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Safely extract a numeric fundamental from yfinance info dict."""
    val = info.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def extract_market_cap_cr(info: dict[str, Any]) -> float:
    """Extract market cap in Indian Crores from yfinance info."""
    raw = extract_fundamental(info, "marketCap")
    return raw / 1e7 if raw > 0 else 0.0
