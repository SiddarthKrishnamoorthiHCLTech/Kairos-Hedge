"""Geopolitical risk analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import GEOPOLITICAL_ANALYST_PROMPT


class GeopoliticalAnalystAgent(BaseAgent):
    """Geopolitical risk and opportunity analysis agent."""

    @property
    def name(self) -> str:
        return "Geopolitical Analyst"

    @property
    def system_prompt(self) -> str:
        return GEOPOLITICAL_ANALYST_PROMPT
