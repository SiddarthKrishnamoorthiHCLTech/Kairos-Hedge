"""Decision engine: entry zone, SL, targets, hold/skip logic."""

from __future__ import annotations

from core.config import AppSettings
from core.logger import get_logger
from core.schemas import AgentOutput, ShortlistItem, Signal, StockDecision
from hedge_fund.engine.debate import compute_debate_strength, detect_disagreements

_log = get_logger(__name__)


def make_decision(
    item: ShortlistItem,
    outputs: list[AgentOutput],
    settings: AppSettings,
) -> StockDecision:
    """Produce final decision for one stock from agent outputs."""
    votes = _tally_votes(outputs)
    disagreements = detect_disagreements(outputs)
    consensus_conf = compute_debate_strength(outputs)
    consensus_signal = _determine_consensus(votes, consensus_conf, settings)
    valid = _is_valid_trade(consensus_signal, votes, consensus_conf, settings)

    entry_zone = ""
    stop_loss = ""
    target_1 = ""
    target_2 = ""
    hold_weeks = ""

    if valid and consensus_signal == Signal.BUY:
        entry_zone, stop_loss, target_1, target_2, hold_weeks = _compute_levels(
            item.current_price, settings
        )

    return StockDecision(
        ticker=item.ticker,
        consensus=consensus_signal,
        consensus_confidence=round(consensus_conf),
        entry_zone=entry_zone,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        hold_weeks=hold_weeks,
        agent_votes={s.value: c for s, c in votes.items()},
        disagreements=disagreements[:5],
        valid_trade=valid,
        agent_outputs=outputs,
    )


def _tally_votes(outputs: list[AgentOutput]) -> dict[Signal, int]:
    """Count agent votes by signal."""
    tally: dict[Signal, int] = {Signal.BUY: 0, Signal.HOLD: 0, Signal.SELL: 0}
    for out in outputs:
        tally[out.signal] = tally.get(out.signal, 0) + 1
    return tally


def _determine_consensus(
    votes: dict[Signal, int],
    confidence: float,
    settings: AppSettings,
) -> Signal:
    """Determine consensus signal from votes and confidence."""
    buy_count = votes.get(Signal.BUY, 0)
    sell_count = votes.get(Signal.SELL, 0)
    if buy_count >= settings.hedge_fund.min_buy_agents:
        return Signal.BUY
    if sell_count > buy_count:
        return Signal.SELL
    return Signal.HOLD


def _is_valid_trade(
    signal: Signal,
    votes: dict[Signal, int],
    confidence: float,
    settings: AppSettings,
) -> bool:
    """Check if trade meets all thresholds."""
    if signal != Signal.BUY:
        return False
    if confidence < settings.hedge_fund.min_consensus_confidence:
        return False
    if votes.get(Signal.BUY, 0) < settings.hedge_fund.min_buy_agents:
        return False
    return True


def _compute_levels(
    price: float,
    settings: AppSettings,
) -> tuple[str, str, str, str, str]:
    """Compute entry zone, stop loss, targets, and hold period."""
    sl_pct = settings.hedge_fund.sl_percent / 100
    t1_pct = settings.hedge_fund.target_1_percent / 100
    t2_pct = settings.hedge_fund.target_2_percent / 100

    entry_low = round(price * 0.99, 2)
    entry_high = round(price * 1.01, 2)
    sl = round(price * (1 - sl_pct), 2)
    t1 = round(price * (1 + t1_pct), 2)
    t2 = round(price * (1 + t2_pct), 2)

    hold_min = settings.hedge_fund.hold_weeks_min
    hold_max = settings.hedge_fund.hold_weeks_max

    return (
        f"₹{entry_low}–{entry_high}",
        f"₹{sl}",
        f"₹{t1}",
        f"₹{t2}",
        f"{hold_min}–{hold_max} weeks",
    )
