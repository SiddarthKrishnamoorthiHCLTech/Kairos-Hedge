"""Portfolio manager aggregation agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import PORTFOLIO_MANAGER_PROMPT


class PortfolioManagerAgent(BaseAgent):
    """Final aggregator agent that synthesises all other agent outputs."""

    @property
    def name(self) -> str:
        return "Portfolio Manager"

    @property
    def system_prompt(self) -> str:
        return PORTFOLIO_MANAGER_PROMPT
