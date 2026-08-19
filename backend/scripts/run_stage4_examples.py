import sys
import os
import json
import psycopg2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.selection.service import PumpRecommendationService

def main():
    conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)

    print("==================================================")
    print("STAGE 4 SAMPLE RECOMMENDATION RUNS")
    print("==================================================")

    # Example A: Sustainable Borehole
    print("\n--- EXAMPLE A: Sustainable Borehole ---")
    res_a = PumpRecommendationService.recommend_borehole(
        conn, yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, delivery_distance_m=100.0, destination_elevation_m=5.0
    )
    print(json.dumps(res_a, indent=2))

    # Example B: High-Abstraction Borehole
    print("\n--- EXAMPLE B: High-Abstraction Borehole ---")
    res_b = PumpRecommendationService.recommend_borehole(
        conn, yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, customer_requested_flow_m3h=9.0, delivery_distance_m=100.0
    )
    print(json.dumps(res_b, indent=2))

    # Example C: Above-Yield Rejection
    print("\n--- EXAMPLE C: Above-Yield Rejection ---")
    res_c = PumpRecommendationService.recommend_borehole(
        conn, yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, customer_requested_flow_m3h=12.0
    )
    print(json.dumps(res_c, indent=2))

    # Example D: Well Default (3.0 m3/h)
    print("\n--- EXAMPLE D: Well Default (3.0 m3/h) ---")
    res_d = PumpRecommendationService.recommend_well(
        conn, static_head_m=20.0, delivery_distance_m=50.0
    )
    print(json.dumps(res_d, indent=2))

    # Example E: Well Customer Flow (5.0 m3/h)
    print("\n--- EXAMPLE E: Well Customer Flow (5.0 m3/h) ---")
    res_e = PumpRecommendationService.recommend_well(
        conn, static_head_m=20.0, customer_requested_flow_m3h=5.0, delivery_distance_m=50.0
    )
    print(json.dumps(res_e, indent=2))

    # Example F: Case Where Multiple Pumps are Viable
    print("\n--- EXAMPLE F: Multiple Viable Pumps ---")
    res_f = PumpRecommendationService.recommend_borehole(
        conn, yield_m3h=8.0, pwl_m=30.0, psd_m=50.0, customer_requested_flow_m3h=3.0, delivery_distance_m=50.0
    )
    print(f"Status: {res_f['status']}")
    print(f"Recommended Pump: {res_f['recommended_pump']['pump_id']} ({res_f['recommended_pump']['pump_name']}), Score: {res_f['recommended_pump']['suitability_score']}")
    print(f"Viable Alternatives Count: {len(res_f['alternatives'])}")

    # Example G: Case Where No Pump is Suitable
    print("\n--- EXAMPLE G: No Suitable Pump ---")
    res_g = PumpRecommendationService.recommend_borehole(
        conn, yield_m3h=10.0, pwl_m=400.0, psd_m=450.0
    )
    print(json.dumps(res_g, indent=2))

    conn.close()

if __name__ == '__main__':
    main()
