"""Abstract base class for all hedge fund AI agents."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from core.exceptions import AgentError
from core.logger import get_logger
from core.schemas import AgentOutput, Signal
from hedge_fund.llm.router import LLMRouter

_log = get_logger(__name__)


class BaseAgent(ABC):
    """Base class every hedge fund agent must inherit from."""

    def __init__(self, llm_router: LLMRouter) -> None:
        self._llm = llm_router

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent display name matching prompts.py key."""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for this agent."""

    async def analyze(self, ticker: str, stock_context: str) -> AgentOutput:
        """Run analysis via LLM and return structured output."""
        user_prompt = self._build_user_prompt(ticker, stock_context)
        try:
            raw = await self._llm.generate(self.system_prompt, user_prompt)
            return self._parse_response(raw)
        except AgentError:
            raise
        except Exception as exc:
            _log.warning(f"Agent {self.name} failed for {ticker}: {exc}")
            return self._fallback_output()

    def _build_user_prompt(self, ticker: str, context: str) -> str:
        """Construct the user prompt with stock data context."""
        return f"Analyze NSE stock: {ticker}\n\nData:\n{context}"

    def _parse_response(self, raw: str) -> AgentOutput:
        """Parse LLM JSON response into AgentOutput."""
        cleaned = self._clean_json(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            _log.warning(f"Agent {self.name} JSON parse failed: {exc}")
            return self._extract_fallback(raw)
        return AgentOutput(
            agent=data.get("agent", self.name),
            signal=self._parse_signal(data.get("signal", "HOLD")),
            confidence=self._clamp_confidence(data.get("confidence", 50)),
            reasoning=data.get("reasoning", "Analysis inconclusive."),
            key_risks=data.get("key_risks", []),
        )

    def _fallback_output(self) -> AgentOutput:
        """Return a neutral HOLD output when agent fails."""
        return AgentOutput(
            agent=self.name,
            signal=Signal.HOLD,
            confidence=30,
            reasoning="Agent could not complete analysis. Defaulting to HOLD.",
            key_risks=["Agent analysis unavailable"],
        )

    def _extract_fallback(self, raw: str) -> AgentOutput:
        """Attempt to extract signal from non-JSON response."""
        upper = raw.upper()
        signal = Signal.HOLD
        if "BUY" in upper and "SELL" not in upper:
            signal = Signal.BUY
        elif "SELL" in upper and "BUY" not in upper:
            signal = Signal.SELL
        return AgentOutput(
            agent=self.name,
            signal=signal,
            confidence=40,
            reasoning=raw[:300] if raw else "Unstructured response.",
            key_risks=["Response was not structured JSON"],
        )

    @staticmethod
    def _clean_json(raw: str) -> str:
        """Strip markdown code fences and whitespace from LLM output."""
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [ln for ln in lines if not ln.strip().startswith("```")]
            text = "\n".join(lines)
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return text[start : end + 1]
        return text

    @staticmethod
    def _parse_signal(raw: str) -> Signal:
        """Parse signal string into Signal enum."""
        upper = str(raw).upper().strip()
        match upper:
            case "BUY":
                return Signal.BUY
            case "SELL":
                return Signal.SELL
            case _:
                return Signal.HOLD

    @staticmethod
    def _clamp_confidence(value: int | float | str) -> int:
        """Clamp confidence to 0–100 range."""
        try:
            v = int(value)
        except (ValueError, TypeError):
            return 50
        return max(0, min(100, v))
