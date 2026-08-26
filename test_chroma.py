import sys
from backend.rag.ingestion import get_chroma_vector_store, DEFAULT_CHROMA_DIR

def main():
    vs = get_chroma_vector_store(DEFAULT_CHROMA_DIR)
    
    print("Testing filter pump_family = 'XYZ999'")
    try:
        res1 = vs.similarity_search("test query", k=2, filter={"pump_family": "XYZ999"})
        print("res1:", res1)
    except Exception as e:
        print("Error 1:", e)
        
    print("Testing filter pump_family in []")
    try:
        res2 = vs.similarity_search("test query", k=2, filter={"pump_family": {"$in": []}})
        print("res2:", res2)
    except Exception as e:
        print("Error 2:", e)

if __name__ == "__main__":
    main()
