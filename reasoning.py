import logfire
from pydantic_ai import Agent
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

data_agent = Agent('google-gla:gemini-flash-latest', 
						system_prompt=(
							"You are a Agentic Data and ML Engineer . "
                                                        "1. Use 'inspect dataset' to see raw data issues. "
                                                        "2. Use search_knowledge_store to find verified fixes in memory. " 
                                                        "3. Follow the ReAct pattern: Reason, Act, Observe."
						),
)


@data_agent.tool
def inspect_datset(ctx) -> str:
	"""Read the raw CSV schema and sample date."""
	df=pd.read_csv('data/retail_store_sales.csv', nrows=10)
	return str({
		"columns" : list(df.columns),
		"missing_values" : df.isnull().sum().to_dict(),
		"types" : [str(t) for t in df.dtypes]
	})

@data_agent.tool
def search_knowledge_store(ctx, search_term: str) -> str:
	"""Fetch verified tranformation recipes from memory _store.json'"""
	with open('memory_store.json','r') as f:
		data = json.load(f)
		# Find recipes where the keyword or issue matches the search term
		matches = [r for r in data['recipes'] if search_term.lower() in r['keyword'].lower()]
		return str(matches) if matches else "No matching recipe found."


async def run_reasoning_cycle():
	#This prompt tests both 01 ( Memory ) and 02 ( Reasoning )
	prompt = "Find a column with a precision issue and suggest a fix from memory."
	result = await data_agent.run(prompt)

	print("\n--- AGENT OUTPUT ---")
	print(result.output)

if __name__ == "__main__":
	import asyncio
	asyncio.run(run_reasoning_cycle())
