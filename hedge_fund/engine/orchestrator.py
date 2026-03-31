"""Orchestrator: runs all 18 agents concurrently per stock."""

from __future__ import annotations

import asyncio

from core.logger import get_logger
from core.schemas import AgentOutput, ShortlistItem
from hedge_fund.agents.ackman import AckmanAgent
from hedge_fund.agents.base_agent import BaseAgent
from hedge_fund.agents.buffett import BuffettAgent
from hedge_fund.agents.burry import BurryAgent
from hedge_fund.agents.cathie_wood import CathieWoodAgent
from hedge_fund.agents.damodaran import DamodaranAgent
from hedge_fund.agents.esg_analyst import ESGAnalystAgent
from hedge_fund.agents.geopolitical_analyst import GeopoliticalAnalystAgent
from hedge_fund.agents.graham import GrahamAgent
from hedge_fund.agents.insider_tracker import InsiderTrackerAgent
from hedge_fund.agents.macro_analyst import MacroAnalystAgent
from hedge_fund.agents.momentum_analyst import MomentumAnalystAgent
from hedge_fund.agents.munger import MungerAgent
from hedge_fund.agents.options_flow import OptionsFlowAgent
from hedge_fund.agents.quant_analyst import QuantAnalystAgent
from hedge_fund.agents.risk_manager import RiskManagerAgent
from hedge_fund.agents.sector_rotation import SectorRotationAgent
from hedge_fund.agents.sentiment_analyst import SentimentAnalystAgent
from hedge_fund.agents.technical_analyst import TechnicalAnalystAgent
from hedge_fund.llm.router import LLMRouter

_log = get_logger(__name__)


def _build_all_agents(router: LLMRouter) -> list[BaseAgent]:
    """Instantiate all 18 debate agents (excluding portfolio manager)."""
    return [
        BuffettAgent(router),
        MungerAgent(router),
        BurryAgent(router),
        CathieWoodAgent(router),
        AckmanAgent(router),
        GrahamAgent(router),
        DamodaranAgent(router),
        TechnicalAnalystAgent(router),
        SentimentAnalystAgent(router),
        MacroAnalystAgent(router),
        RiskManagerAgent(router),
        QuantAnalystAgent(router),
        MomentumAnalystAgent(router),
        OptionsFlowAgent(router),
        InsiderTrackerAgent(router),
        SectorRotationAgent(router),
        ESGAnalystAgent(router),
        GeopoliticalAnalystAgent(router),
    ]


def _build_stock_context(item: ShortlistItem) -> str:
    """Build a text context block for agents from shortlist data."""
    lines = [
        f"Ticker: {item.ticker}",
        f"Company: {item.name}",
        f"Sector: {item.sector}",
        f"Current Price: ₹{item.current_price:.2f}",
        f"Market Cap: ₹{item.market_cap_cr:.0f} Cr",
        f"KAIROS Score: {item.kairos_score}/100",
        f"Relative Strength: {item.rs_rating:.1f}",
        f"Avg Daily Volume: {item.avg_volume:,.0f}",
        "",
        "Framework Scores:",
    ]
    for fw in item.framework_scores:
        lines.append(f"  {fw.framework}: {fw.score:.1f}/100")
    return "\n".join(lines)


async def run_agents_for_stock(
    item: ShortlistItem,
    router: LLMRouter,
) -> list[AgentOutput]:
    """Run all 18 agents concurrently for a single stock."""
    agents = _build_all_agents(router)
    context = _build_stock_context(item)
    _log.info(f"Running {len(agents)} agents for {item.ticker}")

    tasks = [agent.analyze(item.ticker, context) for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    outputs: list[AgentOutput] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            _log.warning(f"Agent {agents[i].name} exception for {item.ticker}: {result}")
            outputs.append(agents[i]._fallback_output())
        elif isinstance(result, AgentOutput):
            outputs.append(result)

    _log.info(f"Completed {len(outputs)} agent analyses for {item.ticker}")
    return outputs
