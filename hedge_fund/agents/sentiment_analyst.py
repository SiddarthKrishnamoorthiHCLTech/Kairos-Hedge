"""Market sentiment analysis agent."""

from __future__ import annotations

from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.llm.prompts import SENTIMENT_ANALYST_PROMPT


class SentimentAnalystAgent(BaseAgent):
    """Market sentiment and mood analysis agent."""

    @property
    def name(self) -> str:
        return "Sentiment Analyst"

    @property
    def system_prompt(self) -> str:
        return SENTIMENT_ANALYST_PROMPT
