import sys
from backend.rag.metadata import detect_pump_family_from_query
from backend.rag.retrieval import retrieve_pump_context
from backend.ai.rag import ask_question

def main():
    print("Testing detect_pump_family_from_query")
    q = "What materials are used in XYZ999 pump?"
    fam, pref = detect_pump_family_from_query(q)
    print(f"fam: {fam}, pref: {pref}")
    
    print("\nTesting retrieve_pump_context for DSS")
    res1 = retrieve_pump_context("What materials are used in DSS pump?", family_prefix="DSS")
    print("sources:", len(res1["sources"]))

    print("\nTesting retrieve_pump_context for DSS (without kwargs)")
    res2 = retrieve_pump_context("What materials are used in DSS pump?", None, "DSS")
    print("sources:", len(res2["sources"]))
    
    print("\nTesting retrieve_pump_context for XYZ999")
    res3 = retrieve_pump_context("What materials are used in XYZ999 pump?", pump_family="XYZ999", family_prefix="XYZ")
    print("sources:", len(res3["sources"]))

if __name__ == "__main__":
    main()
