import chromadb
import pandas as pd
from reasoning import inspect_dataset, search_knowledge_base, apply_transformation

async def pre_flight_check():
    print("--- STARTING LOCAL PRE-FLIGHT CHECK (V2.0 - Vector) ---")

    # 1. Test JSON Memory store (DEACTIVATED)
    # try:
    #     import json
    #     with open('memory_store.json', 'r') as f:
    #         data = json.load(f)
    #         print (f" JSON valid. Found {len(data['recipes'])} recipes.")
    # except Exception as e:
    #     print (f"JSON ERROR: {e}")

    # 2. Test inspect_dataset tool
    try:
        data_info = inspect_dataset(None)
        print("Data Inspection Tool working.")
    except Exception as e:
        print(f"INSPECT TOOL ERROR: {e}")

    # 3. Test NEW search_knowledge_base Tool (Semantic Search)
    try:
        # Testing with a case-insensitive, semantic query
        result = await search_knowledge_base(None, query="FIX THE PRECISION")
        print(f"DEBUG VECTOR SEARCH RESULT: {result[:150]}...") # Printing snippet
        if "Retrieved Recipes" in result:
             print("Semantic Memory Tool (ChromaDB) working.")
    except Exception as e:
        print(f" VECTOR MEMORY TOOL ERROR: {e}")
	
    # 4. Test apply_transformation tool
    try:
        test_code = "df['Price Per Unit'] = df['Price Per Unit'].round(2)"
        res = apply_transformation(None, python_code=test_code)
        if "SUCCESS" in res:
            print("Executioner Tool working.")
        else:
            print(f"Executioner tool failed: {res}")
    except Exception as e:
        print(f"EXECUTIONER ERROR: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(pre_flight_check())
