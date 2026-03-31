"""Benjamin Graham deep value agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import GRAHAM_PROMPT


class GrahamAgent(BaseAgent):
    """Benjamin Graham margin of safety analysis agent."""

    @property
    def name(self) -> str:
        return "Benjamin Graham"

    @property
    def system_prompt(self) -> str:
        return GRAHAM_PROMPT
