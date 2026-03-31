"""Technical analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import TECHNICAL_ANALYST_PROMPT


class TechnicalAnalystAgent(BaseAgent):
    """Technical analysis agent using price action and indicators."""

    @property
    def name(self) -> str:
        return "Technical Analyst"

    @property
    def system_prompt(self) -> str:
        return TECHNICAL_ANALYST_PROMPT
