"""Aswath Damodaran valuation agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import DAMODARAN_PROMPT


class DamodaranAgent(BaseAgent):
    """Aswath Damodaran rigorous valuation analysis agent."""

    @property
    def name(self) -> str:
        return "Aswath Damodaran"

    @property
    def system_prompt(self) -> str:
        return DAMODARAN_PROMPT
