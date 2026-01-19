import logfire
from pydantic_ai.models.google import GoogleModel
from pydantic_ai import Agent, UsageLimits
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

# Initialize the global model without explicitly mentioning the specific model
model = GoogleModel('gemini-flash-latest')

# Updated Agent focusing on strict ReAct behavior and Grounding
data_agent = Agent(
	model=model,
	system_prompt=(
	"""You are an Agentic Data Engineer. Your goal is to clean data using verified recipes.\n"
	### OPERATIONAL PROTOCOL:
	1. INSPECT: Use 'inspect_dataset' to identify data types and issues.
	2. SEARCH STRATEGY: 
   	- When searching the knowledge store, DO NOT use full sentences.
   	- Use strict technical keywords found during inspection (e.g., 'float64', 'int64', 'null', 'Precision').
   	- If a search for a natural term (like 'round') fails, retry ONCE using the data type (like 'float64').
	3. EXECUTION:
   	- Once a recipe is found, call 'apply_transformation' IMMEDIATELY.
   	- If the first execution fails with an error, analyze the error and try to patch the code (e.g., adding .fillna(0)) ONCE.
	4. TERMINATION: Do not exceed 5 tool calls. If the fix isn't applied by then, report the failure.
	"""
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
            "sample_data": df.head(2).to_dict()
        })
    except Exception as e:
        return f"Error reading file: {e}"

@data_agent.tool
def search_knowledge_store(ctx, search_term: str) -> str:
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
        return f"Knowledge store error: {e}"

@data_agent.tool
def apply_transformation(ctx, column_name: str, python_code: str) -> str:
	""" 03 Executioner: Applies the verified recipe to the CSV and saves the cleaned version """
	try:
		#Load the raw data
		file_path = 'data/retail_store_sales.csv'
		df = pd.read_csv(file_path)
	
		# Prepare the execution environment
		# We pass 'df' and 'column_name' into the local scope for the exec() call
		local_scope = {'df' : df, 'col' : column_name}

		# Execute the grounded code (e.g., df[col] =df[col].round(2)
		exec(python_code, {}, local_scope)

		# Retrieve the updated dataframe
		df_cleaned = local_scope['df']

		# Save the result 
		output_path = 'data/retail_store_sales_cleaned.csv'
		df_cleaned.to_csv(output_path, index = False)
		
		return f"SUCCESS: Transformation applied to '{column_name}'. File saved at {output_path}."
	except Exception as e:
		return f"EXECUTION ERROR: {str(e)}"

async def run_reasoning_cycle():
    # UsageLimits protect API quota from infinite loops (O3)
    limits = UsageLimits(request_limit=5, tool_calls_limit=5)

    try:
        # Narrow prompt to prevent the Agent from getting distracted
        prompt = "Identify ONE column with precision issues, find its recipe in memory, and explain the fix."
        
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
