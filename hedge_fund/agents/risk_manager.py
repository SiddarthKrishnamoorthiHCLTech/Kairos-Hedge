"""Risk management agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import RISK_MANAGER_PROMPT


class RiskManagerAgent(BaseAgent):
    """Risk assessment and position sizing agent."""

    @property
    def name(self) -> str:
        return "Risk Manager"

    @property
    def system_prompt(self) -> str:
        return RISK_MANAGER_PROMPT
