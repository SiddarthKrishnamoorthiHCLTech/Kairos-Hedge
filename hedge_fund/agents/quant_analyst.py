"""Quantitative analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import QUANT_ANALYST_PROMPT


class QuantAnalystAgent(BaseAgent):
    """Statistical and factor-based quantitative analysis agent."""

    @property
    def name(self) -> str:
        return "Quant Analyst"

    @property
    def system_prompt(self) -> str:
        return QUANT_ANALYST_PROMPT
