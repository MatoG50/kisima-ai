from typing import List, Dict, Tuple, Set
from collections import Counter
from backend.models.pump import PumpModel, PumpCurvePoint, PhaseOptionEnum

class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.valid_pumps: List[PumpModel] = []
        self.valid_curves: List[PumpCurvePoint] = []
        
        # Summary counts
        self.total_pump_records_found: int = 0
        self.total_curve_points_found: int = 0

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

class PumpValidator:
    @staticmethod
    def validate_dataset(raw_pumps: List[Dict], raw_curves: List[Dict]) -> ValidationResult:
        result = ValidationResult()
        result.total_pump_records_found = len(raw_pumps)
        result.total_curve_points_found = len(raw_curves)
        
        # 1. Validate Pumps
        pump_map: Dict[str, PumpModel] = {}
        seen_pump_ids: Set[str] = set()

        for idx, row in enumerate(raw_pumps, start=2): # 1-indexed header, row starts at 2
            raw_id = row.get('pump_id')
            if not raw_id or str(raw_id).strip() == '':
                result.errors.append(f"Row {idx} [Models]: Missing required 'pump_id'.")
                continue
            
            clean_id = str(raw_id).strip().lower()
            if clean_id in seen_pump_ids:
                result.errors.append(f"Row {idx} [Models]: Duplicate pump_id '{raw_id}'.")
                continue
            seen_pump_ids.add(clean_id)

            pump_name = row.get('pump_name')
            if not pump_name or str(pump_name).strip() == '':
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Missing 'pump_name'.")
                continue
                
            # Numeric parsing & bounds checking
            try:
                motor_kw = float(row.get('motor_kw'))
                if motor_kw <= 0:
                    result.errors.append(f"Row {idx} [Models '{raw_id}']: Invalid motor_kw {motor_kw} <= 0.")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Non-numeric motor_kw '{row.get('motor_kw')}'.")
                continue

            try:
                max_depth_m = float(row.get('max_depth'))
                if max_depth_m <= 0:
                    result.errors.append(f"Row {idx} [Models '{raw_id}']: Invalid max_depth {max_depth_m} <= 0.")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Non-numeric max_depth '{row.get('max_depth')}'.")
                continue

            try:
                discharge_size_in = float(row.get('pipe_size'))
                if discharge_size_in <= 0:
                    result.errors.append(f"Row {idx} [Models '{raw_id}']: Invalid pipe_size {discharge_size_in} <= 0.")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Non-numeric pipe_size '{row.get('pipe_size')}'.")
                continue

            # Phase option parsing
            raw_phase = row.get('phase_option')
            phase_enum = PhaseOptionEnum.from_raw_string(raw_phase)
            if not phase_enum:
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Invalid phase_option '{raw_phase}'.")
                continue

            # FLC currents parsing & checking
            flc_1_val = row.get('FLC_1x240V_A')
            flc_3_val = row.get('FLC_3x415V_A')
            
            flc_1ph_a = None
            if flc_1_val is not None and str(flc_1_val).strip() != '':
                try:
                    flc_1ph_a = float(flc_1_val)
                    if flc_1ph_a <= 0:
                        result.errors.append(f"Row {idx} [Models '{raw_id}']: FLC_1x240V_A must be > 0 (got {flc_1ph_a}).")
                except (ValueError, TypeError):
                    result.errors.append(f"Row {idx} [Models '{raw_id}']: Non-numeric FLC_1x240V_A '{flc_1_val}'.")

            flc_3ph_a = None
            if flc_3_val is not None and str(flc_3_val).strip() != '':
                try:
                    flc_3ph_a = float(flc_3_val)
                    if flc_3ph_a <= 0:
                        result.errors.append(f"Row {idx} [Models '{raw_id}']: FLC_3x415V_A must be > 0 (got {flc_3ph_a}).")
                except (ValueError, TypeError):
                    result.errors.append(f"Row {idx} [Models '{raw_id}']: Non-numeric FLC_3x415V_A '{flc_3_val}'.")

            # Electrical consistency check
            if phase_enum == PhaseOptionEnum.PHASE_1 and flc_1ph_a is None:
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Single-phase pump missing FLC_1x240V_A.")
            if phase_enum == PhaseOptionEnum.PHASE_3 and flc_3ph_a is None:
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Three-phase pump missing FLC_3x415V_A.")
            if phase_enum == PhaseOptionEnum.PHASE_1_3 and (flc_1ph_a is None and flc_3ph_a is None):
                result.errors.append(f"Row {idx} [Models '{raw_id}']: Multi-phase pump missing both FLC_1x240V_A and FLC_3x415V_A.")

            model_obj = PumpModel(
                pump_id=clean_id,
                pump_name=str(pump_name).strip(),
                motor_kw=motor_kw,
                max_depth_m=max_depth_m,
                phase_option=phase_enum,
                flc_1ph_a=flc_1ph_a,
                flc_3ph_a=flc_3ph_a,
                discharge_size_in=discharge_size_in,
                raw_pump_id=str(raw_id).strip()
            )
            pump_map[clean_id] = model_obj
            result.valid_pumps.append(model_obj)

        # 2. Validate Curves
        seen_curve_points: Set[Tuple[str, float]] = set()

        for idx, row in enumerate(raw_curves, start=2):
            raw_id = row.get('pump_id')
            if not raw_id or str(raw_id).strip() == '':
                result.errors.append(f"Row {idx} [Curves]: Missing 'pump_id'.")
                continue

            clean_id = str(raw_id).strip().lower()
            if clean_id not in pump_map:
                result.errors.append(f"Row {idx} [Curves '{raw_id}']: Orphan curve point (no matching pump model '{clean_id}').")
                continue

            try:
                flow_m3h = float(row.get('flow'))
                if flow_m3h < 0:
                    result.errors.append(f"Row {idx} [Curves '{raw_id}']: Flow rate cannot be negative (got {flow_m3h}).")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Curves '{raw_id}']: Non-numeric flow '{row.get('flow')}'.")
                continue

            try:
                head_m = float(row.get('head'))
                if head_m < 0:
                    result.errors.append(f"Row {idx} [Curves '{raw_id}']: Head cannot be negative (got {head_m}).")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Curves '{raw_id}']: Non-numeric head '{row.get('head')}'.")
                continue

            try:
                efficiency_percent = float(row.get('eta'))
                if efficiency_percent < 0 or efficiency_percent > 100:
                    result.errors.append(f"Row {idx} [Curves '{raw_id}']: Efficiency out of range [0..100]% (got {efficiency_percent}).")
            except (ValueError, TypeError):
                result.errors.append(f"Row {idx} [Curves '{raw_id}']: Non-numeric efficiency '{row.get('eta')}'.")
                continue

            point_key = (clean_id, round(flow_m3h, 4))
            if point_key in seen_curve_points:
                result.errors.append(f"Row {idx} [Curves '{raw_id}']: Duplicate curve point at flow={flow_m3h} m3/h.")
                continue
            seen_curve_points.add(point_key)

            curve_obj = PumpCurvePoint(
                pump_id=clean_id,
                flow_m3h=flow_m3h,
                head_m=head_m,
                efficiency_percent=efficiency_percent
            )
            result.valid_curves.append(curve_obj)

        # 3. Relationship Integrity Checks
        curves_per_pump = Counter(pt.pump_id for pt in result.valid_curves)
        for pid in pump_map.keys():
            if curves_per_pump[pid] == 0:
                result.warnings.append(f"Pump model '{pid}' has 0 curve points in performance curves dataset.")

        return result
