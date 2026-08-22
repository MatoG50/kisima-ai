"""
Pump Recommendation Service Entry Point.
Coordinates PostgreSQL data access, engineering rules, per-candidate hydraulic evaluations,
and candidate ranking to return primary pump recommendations and alternative options.
"""

from typing import Dict, Any, Optional, List
from collections import Counter
import psycopg2

from backend.repositories.pump_repository import PumpRepository
from backend.models.pump import PumpModel, PumpCurvePoint
from backend.rules.borehole import evaluate_borehole_application
from backend.rules.well import evaluate_well_application
from backend.engineering.results import AbstractionStatusEnum
from backend.selection.evaluator import evaluate_candidate_pump, EvaluatedCandidate, RejectionReasonEnum
from backend.selection.ranking import rank_candidates

class PumpRecommendationService:
    @staticmethod
    def recommend_borehole(
        conn,
        yield_m3h: float,
        pwl_m: float,
        psd_m: float,
        customer_requested_flow_m3h: Optional[float] = None,
        delivery_distance_m: float = 0.0,
        destination_elevation_m: float = 0.0,
        riser_material: str = "uPVC",
        delivery_material: str = "HDPE"
    ) -> Dict[str, Any]:
        """
        Evaluate all candidate pumps in PostgreSQL for a borehole duty point.
        """
        # 1. Borehole Yield & Abstraction Rules
        borehole_rule_res = evaluate_borehole_application(
            yield_m3h=yield_m3h,
            pwl_m=pwl_m,
            psd_m=psd_m,
            customer_requested_flow_m3h=customer_requested_flow_m3h,
            delivery_distance_m=delivery_distance_m,
            destination_elevation_m=destination_elevation_m
        )

        design_flow = borehole_rule_res.design_flow_m3h

        # 2. Fetch Pumps and Performance Curves from PostgreSQL
        all_pumps = PumpRepository.get_all_pumps(conn)
        curves_map = PumpRepository.get_all_pump_curves_mapped(conn)

        # 3. Candidate Evaluation Loop
        evaluated_candidates: List[EvaluatedCandidate] = []
        rejection_counts = Counter()

        for pump in all_pumps:
            p_curves = curves_map.get(pump.pump_id, [])
            cand_eval = evaluate_candidate_pump(
                pump=pump,
                curves=p_curves,
                pwl_m=pwl_m,
                psd_m=psd_m,
                design_flow_m3h=design_flow,
                delivery_distance_m=delivery_distance_m,
                destination_elevation_m=destination_elevation_m,
                riser_material=riser_material,
                delivery_material=delivery_material
            )
            evaluated_candidates.append(cand_eval)
            if not cand_eval.is_viable and cand_eval.rejection_reason:
                rejection_counts[cand_eval.rejection_reason.value] += 1

        # 4. Rank Viable Candidates
        ranked_viable = rank_candidates(evaluated_candidates)

        warnings = []
        if borehole_rule_res.warning_message:
            warnings.append(borehole_rule_res.warning_message)

        rejection_summary = {
            "total_candidates_evaluated": len(all_pumps),
            "viable_candidates_count": len(ranked_viable),
            "rejected_depth_exceeded": rejection_counts[RejectionReasonEnum.DEPTH_EXCEEDED.value],
            "rejected_out_of_range": rejection_counts[RejectionReasonEnum.OUT_OF_CURVE_RANGE.value],
            "rejected_insufficient_head": rejection_counts[RejectionReasonEnum.INSUFFICIENT_HEAD.value],
            "rejected_inappropriate_flow_class": rejection_counts[RejectionReasonEnum.INAPPROPRIATE_FLOW_CLASS.value]
        }

        # 5. Build Response
        if not ranked_viable:
            return {
                "status": "NO_SUITABLE_PUMP",
                "application_type": "borehole",
                "abstraction_status": borehole_rule_res.abstraction_status.value,
                "design_flow_m3h": design_flow,
                "yield_m3h": yield_m3h,
                "pwl_m": pwl_m,
                "psd_m": psd_m,
                "warnings": warnings,
                "error_message": "No candidate pump in database can satisfy the required duty point and depth constraints.",
                "recommended_pump": None,
                "alternatives": [],
                "rejection_summary": rejection_summary
            }

        rec_pump = ranked_viable[0].to_dict()
        alt_pumps = [c.to_dict() for c in ranked_viable[1:3]]

        return {
            "status": "SUCCESS",
            "application_type": "borehole",
            "abstraction_status": borehole_rule_res.abstraction_status.value,
            "design_flow_m3h": design_flow,
            "yield_m3h": yield_m3h,
            "pwl_m": pwl_m,
            "psd_m": psd_m,
            "destination_elevation_m": destination_elevation_m,
            "delivery_distance_m": delivery_distance_m,
            "warnings": warnings,
            "recommended_pump": rec_pump,
            "alternatives": alt_pumps,
            "rejection_summary": rejection_summary
        }

    @staticmethod
    def recommend_well(
        conn,
        static_head_m: float,
        customer_requested_flow_m3h: Optional[float] = None,
        delivery_distance_m: float = 0.0,
        default_pump_family: str = "DSD",
        delivery_material: str = "HDPE"
    ) -> Dict[str, Any]:
        """
        Evaluate DSD family candidate pumps in PostgreSQL for a well duty point.
        """
        well_rule_res = evaluate_well_application(
            static_head_m=static_head_m,
            customer_requested_flow_m3h=customer_requested_flow_m3h,
            delivery_distance_m=delivery_distance_m,
            default_pump_family=default_pump_family
        )
        design_flow = well_rule_res.design_flow_m3h

        # Fetch only family-matched pumps (e.g. DSD)
        family_pumps = PumpRepository.get_pumps_by_family(conn, default_pump_family)
        curves_map = PumpRepository.get_all_pump_curves_mapped(conn)

        evaluated_candidates: List[EvaluatedCandidate] = []
        rejection_counts = Counter()

        for pump in family_pumps:
            p_curves = curves_map.get(pump.pump_id, [])
            cand_eval = evaluate_candidate_pump(
                pump=pump,
                curves=p_curves,
                pwl_m=static_head_m, # For wells, PWL is static head
                psd_m=0.1,           # Minimal surface installation depth
                design_flow_m3h=design_flow,
                delivery_distance_m=delivery_distance_m,
                destination_elevation_m=0.0,
                delivery_material=delivery_material
            )
            evaluated_candidates.append(cand_eval)
            if not cand_eval.is_viable and cand_eval.rejection_reason:
                rejection_counts[cand_eval.rejection_reason.value] += 1

        ranked_viable = rank_candidates(evaluated_candidates)
        rejection_summary = {
            "total_candidates_evaluated": len(family_pumps),
            "viable_candidates_count": len(ranked_viable),
            "rejected_out_of_range": rejection_counts[RejectionReasonEnum.OUT_OF_CURVE_RANGE.value],
            "rejected_insufficient_head": rejection_counts[RejectionReasonEnum.INSUFFICIENT_HEAD.value],
            "rejected_inappropriate_flow_class": rejection_counts[RejectionReasonEnum.INAPPROPRIATE_FLOW_CLASS.value]
        }

        if not ranked_viable:
            return {
                "status": "NO_SUITABLE_PUMP",
                "application_type": "well",
                "pump_family_filter": default_pump_family,
                "design_flow_m3h": design_flow,
                "is_default_flow_used": well_rule_res.is_default_flow_used,
                "static_head_m": static_head_m,
                "warnings": [],
                "error_message": f"No pump in family '{default_pump_family}' can satisfy the duty point ({design_flow} m3/h @ {static_head_m} m static head).",
                "recommended_pump": None,
                "alternatives": [],
                "rejection_summary": rejection_summary
            }

        rec_pump = ranked_viable[0].to_dict()
        alt_pumps = [c.to_dict() for c in ranked_viable[1:3]]

        return {
            "status": "SUCCESS",
            "application_type": "well",
            "pump_family_filter": default_pump_family,
            "design_flow_m3h": design_flow,
            "is_default_flow_used": well_rule_res.is_default_flow_used,
            "static_head_m": static_head_m,
            "delivery_distance_m": delivery_distance_m,
            "warnings": [],
            "recommended_pump": rec_pump,
            "alternatives": alt_pumps,
            "rejection_summary": rejection_summary
        }
