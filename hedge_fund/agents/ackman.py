"""Bill Ackman activist investing agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import ACKMAN_PROMPT


class AckmanAgent(BaseAgent):
    """Bill Ackman activist investing analysis agent."""

    @property
    def name(self) -> str:
        return "Bill Ackman"

    @property
    def system_prompt(self) -> str:
        return ACKMAN_PROMPT
