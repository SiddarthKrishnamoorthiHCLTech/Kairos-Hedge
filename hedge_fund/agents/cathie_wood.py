"""Cathie Wood disruptive innovation agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import CATHIE_WOOD_PROMPT


class CathieWoodAgent(BaseAgent):
    """Cathie Wood disruptive innovation analysis agent."""

    @property
    def name(self) -> str:
        return "Cathie Wood"

    @property
    def system_prompt(self) -> str:
        return CATHIE_WOOD_PROMPT
