"""
Pump Candidate Evaluation Service.
Bridges PostgreSQL pump specifications with engineering rules to evaluate depth suitability
and calculate hydraulics using the pump's discharge size.
"""

from typing import Optional, Dict, Any, List
import psycopg2
from backend.models.pump import PumpModel
from backend.rules.borehole import evaluate_borehole_application, evaluate_pump_depth_suitability
from backend.rules.well import evaluate_well_application
from backend.engineering.results import BoreholeCalculationResult, WellCalculationResult

class PumpEvaluatorService:
    @staticmethod
    def evaluate_pump_for_borehole(
        pump: PumpModel,
        yield_m3h: float,
        pwl_m: float,
        psd_m: float,
        customer_requested_flow_m3h: Optional[float] = None,
        delivery_distance_m: float = 0.0,
        destination_elevation_m: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate pump against a borehole application duty point.
        Checks depth suitability constraint (PSD <= pump.max_depth_m) and uses
        the pump's discharge_size_in for hydraulic pipe friction calculations.
        """
        # 1. Depth Suitability Check
        is_depth_suitable = evaluate_pump_depth_suitability(psd_m, pump.max_depth_m)

        # 2. Engineering Calculations with pump discharge size
        borehole_res: BoreholeCalculationResult = evaluate_borehole_application(
            yield_m3h=yield_m3h,
            pwl_m=pwl_m,
            psd_m=psd_m,
            customer_requested_flow_m3h=customer_requested_flow_m3h,
            delivery_distance_m=delivery_distance_m,
            destination_elevation_m=destination_elevation_m,
            pipe_diameter_in=pump.discharge_size_in
        )

        res_dict = borehole_res.to_dict()
        res_dict["pump_id"] = pump.pump_id
        res_dict["pump_name"] = pump.pump_name
        res_dict["pump_max_depth_m"] = pump.max_depth_m
        res_dict["pump_discharge_size_in"] = pump.discharge_size_in
        res_dict["is_depth_suitable"] = is_depth_suitable

        if not is_depth_suitable:
            res_dict["depth_unsuitable_reason"] = (
                f"Pump Setting Depth ({psd_m} m) exceeds maximum permitted immersion depth "
                f"({pump.max_depth_m} m) for pump model '{pump.pump_id}'."
            )

        return res_dict

    @staticmethod
    def evaluate_pump_for_well(
        pump: PumpModel,
        static_head_m: float,
        customer_requested_flow_m3h: Optional[float] = None,
        delivery_distance_m: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate pump against a well application duty point.
        """
        well_res: WellCalculationResult = evaluate_well_application(
            static_head_m=static_head_m,
            customer_requested_flow_m3h=customer_requested_flow_m3h,
            delivery_distance_m=delivery_distance_m,
            pipe_diameter_in=pump.discharge_size_in
        )

        res_dict = well_res.to_dict()
        res_dict["pump_id"] = pump.pump_id
        res_dict["pump_name"] = pump.pump_name
        res_dict["pump_discharge_size_in"] = pump.discharge_size_in
        return res_dict
