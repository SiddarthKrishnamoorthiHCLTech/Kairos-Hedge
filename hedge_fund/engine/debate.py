"""Disagreement detection and resolution logic."""

from __future__ import annotations

from core.logger import get_logger
from core.schemas import AgentOutput, Signal

_log = get_logger(__name__)


def detect_disagreements(outputs: list[AgentOutput]) -> list[str]:
    """Identify agents whose signal opposes the majority."""
    vote_counts = _count_votes(outputs)
    majority = _get_majority_signal(vote_counts)
    disagreements: list[str] = []
    for out in outputs:
        if out.signal != majority and out.confidence >= 50:
            summary = f"{out.agent}: {out.reasoning[:80]}"
            disagreements.append(summary)
    return disagreements


def compute_debate_strength(outputs: list[AgentOutput]) -> float:
    """Compute how strong the consensus is (0–100)."""
    if not outputs:
        return 0.0
    vote_counts = _count_votes(outputs)
    majority = _get_majority_signal(vote_counts)
    majority_count = vote_counts.get(majority, 0)
    total = len(outputs)
    strength = (majority_count / total) * 100
    avg_conf = _avg_confidence_for_signal(outputs, majority)
    return round((strength * 0.6 + avg_conf * 0.4), 1)


def _count_votes(outputs: list[AgentOutput]) -> dict[Signal, int]:
    """Count votes by signal type."""
    counts: dict[Signal, int] = {Signal.BUY: 0, Signal.HOLD: 0, Signal.SELL: 0}
    for out in outputs:
        counts[out.signal] = counts.get(out.signal, 0) + 1
    return counts


def _get_majority_signal(vote_counts: dict[Signal, int]) -> Signal:
    """Return the signal with the most votes."""
    return max(vote_counts, key=lambda s: vote_counts[s])


def _avg_confidence_for_signal(outputs: list[AgentOutput], signal: Signal) -> float:
    """Average confidence of agents voting for a specific signal."""
    matching = [o.confidence for o in outputs if o.signal == signal]
    if not matching:
        return 0.0
    return sum(matching) / len(matching)
