"""Macroeconomic analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import MACRO_ANALYST_PROMPT


class MacroAnalystAgent(BaseAgent):
    """Macroeconomic analysis agent for India and global context."""

    @property
    def name(self) -> str:
        return "Macro Analyst"

    @property
    def system_prompt(self) -> str:
        return MACRO_ANALYST_PROMPT
