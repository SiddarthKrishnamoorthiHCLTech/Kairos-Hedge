"""KAIROS screener: orchestrates the full pipeline to produce shortlist.json."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path

from core.config import AppSettings
from core.exceptions import DataError
from core.logger import get_logger
from core.schemas import Shortlist, ShortlistItem
from kairos.data.fetcher import DataFetcher, StockData, extract_market_cap_cr
from kairos.data.universe import UniverseLoader
from kairos.filters.fundamental import apply_fundamental_filters
from kairos.filters.technical import apply_technical_filters
from kairos.scoring.consensus import compute_consensus_score

_log = get_logger(__name__)


async def run_screener(settings: AppSettings) -> Shortlist:
    """Execute the full KAIROS screening pipeline."""
    _log.info("Starting KAIROS screener pipeline")

    symbols = await _load_universe(settings)
    stock_data = await _fetch_all_data(symbols, settings)
    scored = _score_and_filter(stock_data, settings)
    shortlist = _build_shortlist(scored, settings)

    _save_shortlist(shortlist, settings)
    _log.info(f"KAIROS screener complete: {len(shortlist.items)} stocks shortlisted")
    return shortlist


async def _load_universe(settings: AppSettings) -> list[str]:
    """Load NSE stock universe."""
    loader = UniverseLoader(max_symbols=settings.kairos.nse_universe_size)
    symbols = await loader.load()
    _log.info(f"Loaded {len(symbols)} symbols from NSE universe")
    return symbols


async def _fetch_all_data(symbols: list[str], settings: AppSettings) -> list[StockData]:
    """Fetch OHLCV + fundamentals for all symbols."""
    fetcher = DataFetcher(lookback_days=settings.kairos.lookback_days)
    _log.info(f"Fetching data for {len(symbols)} symbols...")

    batch_size = 20
    all_data: list[StockData] = []
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i : i + batch_size]
        results = await fetcher.fetch_batch(batch)
        valid = [r for r in results if r.valid]
        all_data.extend(valid)
        _log.info(f"Fetched batch {i // batch_size + 1}: {len(valid)}/{len(batch)} valid")
        await asyncio.sleep(0.5)

    _log.info(f"Total valid data: {len(all_data)} of {len(symbols)}")
    return all_data


def _score_and_filter(
    stock_data: list[StockData],
    settings: AppSettings,
) -> list[tuple[StockData, float, list]]:
    """Score each stock and apply filters."""
    results: list[tuple[StockData, float, list]] = []

    for sd in stock_data:
        try:
            if not apply_fundamental_filters(sd.info, settings.kairos.min_market_cap_cr):
                continue
            passed_tech, rs_rating = apply_technical_filters(
                sd.ohlcv,
                settings.kairos.min_avg_volume,
            )
            if not passed_tech:
                continue
            score, fw_scores = compute_consensus_score(sd.ohlcv, sd.info)
            if score >= settings.kairos.min_kairos_score:
                results.append((sd, score, fw_scores))
        except Exception as exc:
            _log.debug(f"Scoring failed for {sd.ticker}: {exc}")

    results.sort(key=lambda x: x[1], reverse=True)
    _log.info(f"Scored and filtered: {len(results)} stocks passed all criteria")
    return results


def _build_shortlist(
    scored: list[tuple[StockData, float, list]],
    settings: AppSettings,
) -> Shortlist:
    """Build the final shortlist from scored results."""
    items: list[ShortlistItem] = []
    top_n = settings.kairos.top_n_shortlist

    for sd, score, fw_scores in scored[:top_n]:
        item = ShortlistItem(
            ticker=sd.ticker,
            name=sd.info.get("shortName", sd.ticker),
            sector=sd.info.get("sector", "Unknown"),
            kairos_score=round(score, 1),
            framework_scores=fw_scores,
            market_cap_cr=round(extract_market_cap_cr(sd.info), 1),
            avg_volume=round(sd.ohlcv["Volume"].tail(20).mean(), 0),
            current_price=round(float(sd.ohlcv["Close"].iloc[-1]), 2),
            rs_rating=round(score, 1),
        )
        items.append(item)

    return Shortlist(
        date=date.today(),
        items=items,
        universe_size=settings.kairos.nse_universe_size,
        filtered_count=len(scored),
    )


def _save_shortlist(shortlist: Shortlist, settings: AppSettings) -> None:
    """Save shortlist to JSON file."""
    output_dir = Path(settings.output.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "shortlist.json"
    output_path.write_text(shortlist.model_dump_json(indent=2), encoding="utf-8")
    _log.info(f"Shortlist saved to {output_path}")
