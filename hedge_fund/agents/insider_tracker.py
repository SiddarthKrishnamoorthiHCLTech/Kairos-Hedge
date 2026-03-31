"""Insider and promoter activity tracking agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import INSIDER_TRACKER_PROMPT


class InsiderTrackerAgent(BaseAgent):
    """Insider, promoter, and bulk deal tracking agent."""

    @property
    def name(self) -> str:
        return "Insider Tracker"

    @property
    def system_prompt(self) -> str:
        return INSIDER_TRACKER_PROMPT
