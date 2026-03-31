"""ESG and corporate governance analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import ESG_ANALYST_PROMPT


class ESGAnalystAgent(BaseAgent):
    """ESG and corporate governance quality agent."""

    @property
    def name(self) -> str:
        return "ESG Analyst"

    @property
    def system_prompt(self) -> str:
        return ESG_ANALYST_PROMPT
