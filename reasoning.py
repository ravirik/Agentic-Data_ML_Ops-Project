import logfire
import chromadb
from pydantic_ai.models.google import GoogleModel
from pydantic_ai import Agent, RunContext, UsageLimits
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Logfire with environment control
logfire.configure(
    send_to_logfire=os.getenv('LOGFIRE_ENABLED', 'true').lower() == 'true'
)
logfire.instrument_pydantic_ai()

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="transformation_recipes")

# Initialize the global model without explicitly mentioning the specific model
model = GoogleModel('gemini-flash-latest')

# Reasoning Engine ( Agent Configuration )
data_agent = Agent(
	model=model,
	system_prompt=(
        "You are an Agentic Data Engineer. Goal: Clean data using Semantic RAG.\n"
        "### OPERATIONAL PROTOCOL (Strict 5 RPM Limit):\n"
        "1. BATCH INSPECT: Use 'inspect_dataset' to identify ALL column issues at once.\n"
        "2. SEMANTIC SEARCH: Use 'search_knowledge_base' to find similar solutions. "
        "   The retrieved code is a HINT; adapt it to the actual column names in the CSV.\n"
        "3. ONE-SHOT EXECUTION: Write one Python script to fix all identified issues in one call.\n"
        "4. TERMINATION: Complete the task in 3 tool calls or less to stay under quota."
    ),
)

@data_agent.tool
def inspect_dataset(ctx) -> str:
    """Read the raw CSV schema and sample data to identify issues."""
    try:
        # Ensuring we use the correct path and return a readable summary
        df = pd.read_csv('data/retail_store_sales.csv', nrows=10)
        return str({
            "columns": list(df.columns),
            "types": {col: str(t) for col, t in zip(df.columns, df.dtypes)},
            "sample_data": df.head(3).to_dict()
        })
    except Exception as e:
        return f"File error: {e}"


""" DEACTIVATED OLD JSON SEARCH """

''' @data_agent.tool
def search_knowledge_store(ctx, search_term : str) -> str:
    """Fetch verified transformation recipes from memory_store.json."""
    try:
       with open('memory_store.json', 'r') as f:
            data = json.load(f)
        
        search_term_clean = search_term.lower()
        matches = []
        
        for r in data['recipes']:
            # Aligned with specific JSON keys: issue, keyword, explanation
            issue_val = r.get('issue', '').lower()
            keyword_val = r.get('keyword', '').lower()
            explanation_val = r.get('explanation', '').lower()
            
            if (search_term_clean in issue_val or 
               search_term_clean in keyword_val or 
                search_term_clean in explanation_val):
               matches.append(r)

        if matches:
            # Format the output clearly so the LLM doesn't miss the 'solution' key
           formatted_results = "\n".join([
                f"RECIPE: {m['issue']}\nCODE: {m['solution']}\nEXPLANATION: {m['explanation']}" 
               for m in matches
            ])
            return f"FOUND THE FOLLOWING RECIPES:\n{formatted_results}"
        
        return f"No matching recipe found for '{search_term}'."
    except Exception as e:
        return f"Knowledge store error: {e}" '''


""" ACTIVE NEW SEMANTIC SEARCH """
@data_agent.tool
async def search_knowledge_base(ctx: RunContext[str], query: str) -> str:
    """
    Search the vector database for data engineering solutions.
    Use this to find recipes for issues like precision, nulls or formatting.
    """
    try:
        # Fetch top 3 results to save RPM by giving the LLM more context at once
        results = collection.query(query_texts=[query], n_results = 3)

        if not results['documents'][0]:
            return "No specific recipes found. Rely on your internal python knowledge."
        
        context = "Retrieved recipes from Memory:\n"
        for i, (doc, meta) in enumerate (zip(results['documents'][0], results['metadatas'][0])):
            context += f"{i+1}. Issue : {doc}\n Solution Hint:{meta['solution']} "
        return context

    except Exception as e:
        return f"Vector DB Error: {e}"

@data_agent.tool
def apply_transformation(ctx, python_code: str) -> str:
	"""  Executioner: Applies the synthesized code to the CSV and saves the cleaned version """
	try:
		#Load the raw data
		file_path = 'data/retail_store_sales.csv'
		df = pd.read_csv(file_path)
	
		# Prepare the execution environment: pass 'df' for the exec() call
		local_scope = {'df': df}

		# Execute the grounded code (e.g., df['Unit_Price'] = df['Unit_Price'].round(2))
		exec(python_code, {}, local_scope)

		# Retrieve the updated dataframe
		df_cleaned = local_scope['df']

		# Save the result
		output_path = 'data/retail_store_sales_cleaned.csv'
		df_cleaned.to_csv(output_path, index=False)

		return f"SUCCESS: Transformation applied. File saved at {output_path}."
	except Exception as e:
		return f"EXECUTION ERROR: {str(e)}"


# --- EXECUTION LOOP ---

async def run_reasoning_cycle():
    # UsageLimits protect API quota from infinite loops (Guardrails)
    limits = UsageLimits(request_limit=5, tool_calls_limit=5)

    try:
        prompt = "Inspect the dataset, find all columns needing decimal rounding, search for solutions, and apply the fix."
        
        result = await data_agent.run(prompt, usage_limits=limits)

        print("\n--- AGENT OUTPUT ---")
        print(result.output)
        
    except Exception as e:
        # This will catch the 429 error or the limit hit
        print(f"\n[!] Reasoning Cycle Stopped: {e}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_reasoning_cycle())
    finally:
        # Give logfire time to flush the final trace
        print("Closing Logfire connection...")
