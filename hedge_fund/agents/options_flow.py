"""Options flow analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import OPTIONS_FLOW_PROMPT


class OptionsFlowAgent(BaseAgent):
    """NSE derivatives and options flow analysis agent."""

    @property
    def name(self) -> str:
        return "Options Flow Analyst"

    @property
    def system_prompt(self) -> str:
        return OPTIONS_FLOW_PROMPT
