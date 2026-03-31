"""Weighted score aggregation across all KAIROS scoring frameworks."""

from __future__ import annotations

import pandas as pd

from core.logger import get_logger
from core.schemas import StockScore
from kairos.scoring.frameworks.base_framework import BaseFramework
from kairos.scoring.frameworks.buffett import BuffettFramework
from kairos.scoring.frameworks.graham import GrahamFramework
from kairos.scoring.frameworks.growth import GrowthFramework
from kairos.scoring.frameworks.lynch import LynchFramework
from kairos.scoring.frameworks.minervini import MinerviniFramework
from kairos.scoring.frameworks.momentum import MomentumFramework
from kairos.scoring.frameworks.oneil import ONeilFramework
from kairos.scoring.frameworks.quality import QualityFramework
from kairos.scoring.frameworks.value import ValueFramework
from kairos.scoring.frameworks.weinstein import WeinsteinFramework
from kairos.scoring.frameworks.wyckoff import WyckoffFramework

_log = get_logger(__name__)


def _all_frameworks() -> list[BaseFramework]:
    """Instantiate all scoring frameworks."""
    return [
        MinerviniFramework(),
        ONeilFramework(),
        WeinsteinFramework(),
        WyckoffFramework(),
        BuffettFramework(),
        GrahamFramework(),
        LynchFramework(),
        MomentumFramework(),
        ValueFramework(),
        GrowthFramework(),
        QualityFramework(),
    ]


def compute_consensus_score(
    ohlcv: pd.DataFrame,
    info: dict,
    frameworks: list[BaseFramework] | None = None,
) -> tuple[float, list[StockScore]]:
    """Compute weighted consensus score across all frameworks."""
    active_frameworks = frameworks or _all_frameworks()
    scores: list[StockScore] = []
    weighted_sum = 0.0
    total_weight = 0.0

    for fw in active_frameworks:
        try:
            result = fw.score(ohlcv, info)
            scores.append(result)
            weighted_sum += result.score * fw.weight
            total_weight += fw.weight
        except Exception as exc:
            _log.warning(f"Framework {fw.name} failed: {exc}")

    consensus = (weighted_sum / total_weight * 100) if total_weight > 0 else 0.0
    consensus = max(0.0, min(100.0, consensus))
    _log.debug(f"Consensus score: {consensus:.1f} from {len(scores)} frameworks")
    return consensus, scores
