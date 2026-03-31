"""Momentum analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import MOMENTUM_ANALYST_PROMPT


class MomentumAnalystAgent(BaseAgent):
    """Multi-timeframe momentum analysis agent."""

    @property
    def name(self) -> str:
        return "Momentum Analyst"

    @property
    def system_prompt(self) -> str:
        return MOMENTUM_ANALYST_PROMPT
