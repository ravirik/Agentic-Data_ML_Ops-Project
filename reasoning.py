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
        "You are a Grounded Data Engineer. Follow the ReAct pattern: Reason, Act, Observe.\n"
        "1. First, call 'inspect_dataset' to identify issues.\n"
        "2. Second, identify the specific data type of the problem column.\n"
        "3. Third, use 'search_knowledge_store' using that data type as the keyword.\n"
        "4. DO NOT suggest a fix until you have a match from the knowledge store.\n"
        "5. Limit your reasoning to ONE specific column issue at a time."
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
            # Return the whole recipe object so the Agent sees the 'solution'
            return str(matches)
        
        return f"No matching recipe found for '{search_term}'."
    except Exception as e:
        return f"Knowledge store error: {e}"

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
