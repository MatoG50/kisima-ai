from typing import List, Dict, Tuple, Optional
import psycopg2
from psycopg2.extras import execute_values
from backend.models.pump import PumpModel, PumpCurvePoint, PhaseOptionEnum

class PumpRepository:
    @staticmethod
    def get_all_pumps(conn) -> List[PumpModel]:
        """Fetch all pump specification records from PostgreSQL."""
        sql = """
        SELECT pump_id, pump_name, motor_kw, max_depth_m, phase_option,
               flc_1ph_a, flc_3ph_a, discharge_size_in, raw_pump_id
        FROM pumps
        ORDER BY pump_id ASC;
        """
        pumps = []
        with conn.cursor() as cur:
            cur.execute(sql)
            for row in cur.fetchall():
                pumps.append(PumpModel(
                    pump_id=row[0],
                    pump_name=row[1],
                    motor_kw=float(row[2]),
                    max_depth_m=float(row[3]),
                    phase_option=PhaseOptionEnum.from_raw_string(row[4]),
                    flc_1ph_a=float(row[5]) if row[5] is not None else None,
                    flc_3ph_a=float(row[6]) if row[6] is not None else None,
                    discharge_size_in=float(row[7]),
                    raw_pump_id=row[8]
                ))
        return pumps

    @staticmethod
    def get_pumps_by_family(conn, family_prefix: str) -> List[PumpModel]:
        """Fetch pumps belonging to a specific family (e.g. 'dsd')."""
        prefix_pattern = f"{family_prefix.strip().lower()}%"
        sql = """
        SELECT pump_id, pump_name, motor_kw, max_depth_m, phase_option,
               flc_1ph_a, flc_3ph_a, discharge_size_in, raw_pump_id
        FROM pumps
        WHERE LOWER(pump_id) LIKE %s OR LOWER(pump_name) LIKE %s
        ORDER BY pump_id ASC;
        """
        pumps = []
        with conn.cursor() as cur:
            cur.execute(sql, (prefix_pattern, f"%{family_prefix.strip().lower()}%"))
            for row in cur.fetchall():
                pumps.append(PumpModel(
                    pump_id=row[0],
                    pump_name=row[1],
                    motor_kw=float(row[2]),
                    max_depth_m=float(row[3]),
                    phase_option=PhaseOptionEnum.from_raw_string(row[4]),
                    flc_1ph_a=float(row[5]) if row[5] is not None else None,
                    flc_3ph_a=float(row[6]) if row[6] is not None else None,
                    discharge_size_in=float(row[7]),
                    raw_pump_id=row[8]
                ))
        return pumps

    @staticmethod
    def get_pump_curves(conn, pump_id: str) -> List[PumpCurvePoint]:
        """Fetch curve points for a specific pump_id sorted by flow_m3h ASC."""
        sql = """
        SELECT pump_id, flow_m3h, head_m, efficiency_percent, id
        FROM pump_curves
        WHERE pump_id = %s
        ORDER BY flow_m3h ASC;
        """
        points = []
        with conn.cursor() as cur:
            cur.execute(sql, (pump_id.strip().lower(),))
            for row in cur.fetchall():
                points.append(PumpCurvePoint(
                    pump_id=row[0],
                    flow_m3h=float(row[1]),
                    head_m=float(row[2]),
                    efficiency_percent=float(row[3]),
                    id=row[4]
                ))
        return points

    @staticmethod
    def get_all_pump_curves_mapped(conn) -> Dict[str, List[PumpCurvePoint]]:
        """Fetch all performance curve points mapped by pump_id."""
        sql = """
        SELECT pump_id, flow_m3h, head_m, efficiency_percent, id
        FROM pump_curves
        ORDER BY pump_id ASC, flow_m3h ASC;
        """
        curves_map: Dict[str, List[PumpCurvePoint]] = {}
        with conn.cursor() as cur:
            cur.execute(sql)
            for row in cur.fetchall():
                pid = row[0]
                pt = PumpCurvePoint(
                    pump_id=pid,
                    flow_m3h=float(row[1]),
                    head_m=float(row[2]),
                    efficiency_percent=float(row[3]),
                    id=row[4]
                )
                if pid not in curves_map:
                    curves_map[pid] = []
                curves_map[pid].append(pt)
        return curves_map

    @staticmethod
    def upsert_pumps(conn, pumps: List[PumpModel]) -> Tuple[int, int]:
        if not pumps:
            return 0, 0

        with conn.cursor() as cur:
            cur.execute("SELECT pump_id FROM pumps;")
            existing_ids = set(row[0] for row in cur.fetchall())

        inserted_count = sum(1 for p in pumps if p.pump_id not in existing_ids)
        updated_count = len(pumps) - inserted_count

        sql = """
        INSERT INTO pumps (
            pump_id, pump_name, motor_kw, max_depth_m, phase_option,
            flc_1ph_a, flc_3ph_a, discharge_size_in, raw_pump_id, updated_at
        ) VALUES %s
        ON CONFLICT (pump_id) DO UPDATE SET
            pump_name = EXCLUDED.pump_name,
            motor_kw = EXCLUDED.motor_kw,
            max_depth_m = EXCLUDED.max_depth_m,
            phase_option = EXCLUDED.phase_option,
            flc_1ph_a = EXCLUDED.flc_1ph_a,
            flc_3ph_a = EXCLUDED.flc_3ph_a,
            discharge_size_in = EXCLUDED.discharge_size_in,
            raw_pump_id = EXCLUDED.raw_pump_id,
            updated_at = CURRENT_TIMESTAMP;
        """

        records = [
            (
                p.pump_id,
                p.pump_name,
                p.motor_kw,
                p.max_depth_m,
                p.phase_option.value,
                p.flc_1ph_a,
                p.flc_3ph_a,
                p.discharge_size_in,
                p.raw_pump_id,
                'NOW()'
            )
            for p in pumps
        ]

        with conn.cursor() as cur:
            execute_values(cur, sql, records, page_size=200)
        conn.commit()

        return inserted_count, updated_count

    @staticmethod
    def upsert_curves(conn, curves: List[PumpCurvePoint]) -> Tuple[int, int]:
        if not curves:
            return 0, 0

        with conn.cursor() as cur:
            cur.execute("SELECT pump_id, flow_m3h FROM pump_curves;")
            existing_points = set((row[0], float(row[1])) for row in cur.fetchall())

        inserted_count = sum(1 for c in curves if (c.pump_id, round(c.flow_m3h, 2)) not in existing_points)
        updated_count = len(curves) - inserted_count

        sql = """
        INSERT INTO pump_curves (
            pump_id, flow_m3h, head_m, efficiency_percent, updated_at
        ) VALUES %s
        ON CONFLICT (pump_id, flow_m3h) DO UPDATE SET
            head_m = EXCLUDED.head_m,
            efficiency_percent = EXCLUDED.efficiency_percent,
            updated_at = CURRENT_TIMESTAMP;
        """

        records = [
            (
                c.pump_id,
                c.flow_m3h,
                c.head_m,
                c.efficiency_percent,
                'NOW()'
            )
            for c in curves
        ]

        with conn.cursor() as cur:
            execute_values(cur, sql, records, page_size=500)
        conn.commit()

        return inserted_count, updated_count

    @staticmethod
    def get_summary_counts(conn) -> Dict[str, int]:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pumps;")
            total_pumps = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM pump_curves;")
            total_curves = cur.fetchone()[0]
        return {
            "total_pumps": total_pumps,
            "total_curves": total_curves
        }
