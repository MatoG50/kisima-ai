"""
Deterministic Candidate Ranking and Scoring Engine Module.
Ranks viable candidate pumps using configurable, transparent scoring weights.
"""

from typing import List
from backend.selection.evaluator import EvaluatedCandidate

DEFAULT_WEIGHT_EFFICIENCY: float = 0.35
DEFAULT_WEIGHT_MARGIN: float = 0.30
DEFAULT_WEIGHT_MOTOR: float = 0.20
DEFAULT_WEIGHT_BEP: float = 0.15

def rank_candidates(
    candidates: List[EvaluatedCandidate],
    weight_efficiency: float = DEFAULT_WEIGHT_EFFICIENCY,
    weight_margin: float = DEFAULT_WEIGHT_MARGIN,
    weight_motor: float = DEFAULT_WEIGHT_MOTOR,
    weight_bep: float = DEFAULT_WEIGHT_BEP
) -> List[EvaluatedCandidate]:
    """
    Rank viable candidate pumps deterministically by calculating a composite suitability score [0..100].
    Updates candidates in-place with suitability_score and returns viable candidates sorted descending by score.
    """
    viable_candidates = [c for c in candidates if c.is_viable]
    if not viable_candidates:
        return []

    # Calculate min/max reference bounds across viable candidates
    max_eta = max(c.operating_efficiency_percent for c in viable_candidates)
    min_kw = min(c.pump.motor_kw for c in viable_candidates)

    for c in viable_candidates:
        # 1. Efficiency Sub-Score (35%)
        s_eta = (c.operating_efficiency_percent / max_eta * 100.0) if max_eta > 0 else 0.0

        # 2. Head Margin Sub-Score (30%) - Ideal margin ratio is ~10% over TDH
        margin_ratio = (c.head_margin_m / c.required_tdh_m) if c.required_tdh_m > 0 else 0.0
        s_margin = max(0.0, 100.0 - 300.0 * abs(margin_ratio - 0.10))

        # 3. Motor Power Sub-Score (20%) - Rewards appropriate motor sizing
        s_motor = (min_kw / c.pump.motor_kw * 100.0) if c.pump.motor_kw > 0 else 0.0

        # 4. BEP Proximity Sub-Score (15%) - Operating flow proximity to BEP flow
        if c.bep_flow_m3h > 0:
            flow_diff_ratio = abs(c.design_flow_m3h - c.bep_flow_m3h) / c.bep_flow_m3h
            s_bep = max(0.0, 100.0 - 200.0 * flow_diff_ratio)
        else:
            s_bep = 50.0

        total_score = (
            weight_efficiency * s_eta +
            weight_margin * s_margin +
            weight_motor * s_motor +
            weight_bep * s_bep
        )
        c.suitability_score = round(total_score, 2)

    # Sort descending by score
    sorted_viable = sorted(viable_candidates, key=lambda c: c.suitability_score, reverse=True)
    return sorted_viable
