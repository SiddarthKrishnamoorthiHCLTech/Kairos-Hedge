"""Charlie Munger mental models agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import MUNGER_PROMPT


class MungerAgent(BaseAgent):
    """Charlie Munger inversion and mental models agent."""

    @property
    def name(self) -> str:
        return "Charlie Munger"

    @property
    def system_prompt(self) -> str:
        return MUNGER_PROMPT
