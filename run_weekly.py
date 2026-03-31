"""KAIROS-HEDGE: Weekly trading intelligence system entry point."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import date
from pathlib import Path

from core.config import AppSettings, load_settings
from core.exceptions import KairosError
from core.logger import get_logger
from core.schemas import Shortlist, StockDecision, WeeklyReport
from hedge_fund.engine.decision import make_decision
from hedge_fund.engine.orchestrator import run_agents_for_stock
from hedge_fund.llm.router import LLMRouter
from kairos.screener import run_screener
from notifier.formatter import format_telegram_message, save_html_report
from notifier.telegram import send_telegram_message

_log = get_logger(__name__)


async def main() -> None:
    """Execute the full KAIROS-HEDGE weekly pipeline."""
    _log.info("=" * 60)
    _log.info("KAIROS-HEDGE Weekly Pipeline Starting")
    _log.info("=" * 60)

    settings = load_settings()
    _ensure_output_dirs(settings)

    shortlist = await _run_kairos(settings)
    if not shortlist.items:
        await _handle_skip_week(settings)
        return

    decisions = await _run_hedge_fund(shortlist, settings)
    report = _build_report(shortlist, decisions, settings)

    await _deliver_results(report, settings)
    _log.info("KAIROS-HEDGE Weekly Pipeline Complete ✅")


async def _run_kairos(settings: AppSettings) -> Shortlist:
    """Run the KAIROS screener module."""
    _log.info("─── MODULE 1: KAIROS SCREENER ───")
    try:
        return await run_screener(settings)
    except KairosError as exc:
        _log.error(f"KAIROS screener failed: {exc}")
        return Shortlist(date=date.today())


async def _run_hedge_fund(shortlist: Shortlist, settings: AppSettings) -> list[StockDecision]:
    """Run the Hedge Fund debate engine on shortlisted stocks."""
    _log.info("─── MODULE 2: HEDGE FUND DEBATE ENGINE ───")
    router = LLMRouter(settings)
    decisions: list[StockDecision] = []

    for item in shortlist.items:
        _log.info(f"Analyzing {item.ticker} ({item.name})...")
        try:
            outputs = await run_agents_for_stock(item, router)
            decision = make_decision(item, outputs, settings)
            decisions.append(decision)
            _log.info(f"{item.ticker}: {decision.consensus.value} (confidence: {decision.consensus_confidence}%)")
        except KairosError as exc:
            _log.error(f"Hedge Fund failed for {item.ticker}: {exc}")

    return decisions


def _build_report(
    shortlist: Shortlist,
    decisions: list[StockDecision],
    settings: AppSettings,
) -> WeeklyReport:
    """Build the final weekly report."""
    valid = [d for d in decisions if d.valid_trade]
    skip = len(valid) == 0
    return WeeklyReport(
        date=date.today(),
        shortlist=shortlist,
        decisions=decisions,
        valid_trades=len(valid),
        total_screened=len(decisions),
        skip_week=skip,
        skip_message=settings.trading.skip_week_message if skip else "",
    )


async def _deliver_results(report: WeeklyReport, settings: AppSettings) -> None:
    """Save outputs and send notifications."""
    _log.info("─── DELIVERING RESULTS ───")

    if settings.output.save_json:
        _save_json(report, settings)

    if settings.output.save_html_report:
        save_html_report(report, settings.output.archive_dir)

    if settings.output.send_telegram:
        message = format_telegram_message(report)
        await send_telegram_message(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
            message,
        )


async def _handle_skip_week(settings: AppSettings) -> None:
    """Handle case where no stocks pass screening."""
    _log.info("No stocks passed KAIROS screening — skip week")
    report = WeeklyReport(
        date=date.today(),
        shortlist=Shortlist(date=date.today()),
        skip_week=True,
        skip_message=settings.trading.skip_week_message,
    )
    await _deliver_results(report, settings)


def _save_json(report: WeeklyReport, settings: AppSettings) -> None:
    """Save weekly report as JSON."""
    output_dir = Path(settings.output.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "weekly_report.json"
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    _log.info(f"Weekly report JSON saved to {path}")


def _ensure_output_dirs(settings: AppSettings) -> None:
    """Create output directories if they don't exist."""
    Path(settings.output.output_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output.archive_dir).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _log.info("Pipeline interrupted by user")
        sys.exit(0)
    except KairosError as exc:
        _log.error(f"Pipeline failed: {exc}")
        sys.exit(1)
