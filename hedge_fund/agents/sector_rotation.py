"""Sector rotation analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import SECTOR_ROTATION_PROMPT


class SectorRotationAgent(BaseAgent):
    """Sector rotation and fund flow analysis agent."""

    @property
    def name(self) -> str:
        return "Sector Rotation Analyst"

    @property
    def system_prompt(self) -> str:
        return SECTOR_ROTATION_PROMPT
