"""Warren Buffett value investing agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import BUFFETT_PROMPT


class BuffettAgent(BaseAgent):
    """Warren Buffett deep value analysis agent."""

    @property
    def name(self) -> str:
        return "Warren Buffett"

    @property
    def system_prompt(self) -> str:
        return BUFFETT_PROMPT
