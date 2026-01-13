import logfire
from pydantic_ai import Agent
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

data_agent = Agent('google-gla:gemini-flash-latest', 
						system_prompt=(
							"You are a Agentic Data Engineer. Your goal is to inspect raw data"
							"and 'Fragility' in the pipeline."
							"Follow the ReAct pattern: Reason about the data, suggest an Action,"
							"and explain what you expect to observe."
						),
)

def get_data_summary():
	"""Tool to read the first few rows and schema of the dataset."""
	file_path='data/retail_store_sales.csv'
	if not os.path.exists(file_path):
		return "Error: File not found"
	df=pd.read_csv(file_path, nrows=10)
	summary= {
		"colums":list(df.columns),
		"sample_data": df.head(5).to_dict(),
		"missing_values":df.isnull().sum().to_dict(),
		"data_types":list(df.dtypes)
	}
	return str(summary)

@data_agent.tool

def inspect_datset(ctx) -> str:
	""" Provides the datset with actual schema and sample of dirty data."""
	return get_data_summary()

async def run_reasoning_cycle():
	#The "thought" trigger
	user_prompt = "Inspect the retail dataset and find 3 issues that could break a SQL pipeline or create further hindrance in creating data pipelines"
	result = await data_agent.run(user_prompt)

	print("\n--- AGENT REASONING (02) ---")
	print(result.output)

if __name__ == "__main__":
	import asyncio
	asyncio.run(run_reasoning_cycle())
