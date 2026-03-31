"""Simple backtester: CAGR, max drawdown, Sharpe, Sortino, win rate."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from core.logger import get_logger

_log = get_logger(__name__)


@dataclass(slots=True)
class BacktestResult:
    """Container for backtest performance metrics."""

    cagr_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    win_rate_pct: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0


def compute_cagr(start_val: float, end_val: float, years: float) -> float:
    """Compute compound annual growth rate."""
    if start_val <= 0 or years <= 0:
        return 0.0
    return ((end_val / start_val) ** (1.0 / years) - 1) * 100


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """Compute maximum drawdown percentage from equity curve."""
    if equity_curve.empty:
        return 0.0
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak * 100
    return float(drawdown.min())


def compute_sharpe(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    """Compute annualised Sharpe ratio."""
    if returns.empty or returns.std() == 0:
        return 0.0
    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf
    return float(excess.mean() / excess.std() * (252 ** 0.5))


def compute_sortino(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    """Compute annualised Sortino ratio."""
    if returns.empty:
        return 0.0
    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf
    downside = excess[excess < 0]
    if downside.empty or downside.std() == 0:
        return 0.0
    return float(excess.mean() / downside.std() * (252 ** 0.5))


def compute_win_rate(trade_returns: list[float]) -> float:
    """Compute win rate from list of trade P&L percentages."""
    if not trade_returns:
        return 0.0
    wins = sum(1 for r in trade_returns if r > 0)
    return (wins / len(trade_returns)) * 100


def run_backtest(equity_curve: pd.Series, trade_returns: list[float]) -> BacktestResult:
    """Run full backtest metrics computation."""
    if equity_curve.empty:
        return BacktestResult()
    daily_returns = equity_curve.pct_change().dropna()
    years = len(equity_curve) / 252 if len(equity_curve) > 0 else 1.0
    start_val = float(equity_curve.iloc[0])
    end_val = float(equity_curve.iloc[-1])
    wins = [r for r in trade_returns if r > 0]
    losses = [r for r in trade_returns if r <= 0]

    return BacktestResult(
        cagr_pct=round(compute_cagr(start_val, end_val, years), 2),
        max_drawdown_pct=round(compute_max_drawdown(equity_curve), 2),
        sharpe_ratio=round(compute_sharpe(daily_returns), 2),
        sortino_ratio=round(compute_sortino(daily_returns), 2),
        win_rate_pct=round(compute_win_rate(trade_returns), 2),
        total_trades=len(trade_returns),
        winning_trades=len(wins),
        losing_trades=len(losses),
    )
