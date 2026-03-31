"""Michael Burry contrarian value agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import BURRY_PROMPT


class BurryAgent(BaseAgent):
    """Michael Burry contrarian deep-value agent."""

    @property
    def name(self) -> str:
        return "Michael Burry"

    @property
    def system_prompt(self) -> str:
        return BURRY_PROMPT
