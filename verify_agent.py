import os
import logfire
from pydantic_ai import Agent
from dotenv import load_dotenv

logfire.configure()
logfire.instrument_pydantic_ai()

load_dotenv()

agent = Agent('google-gla:gemini-flash-latest', system_prompt = "Tell me the system status.")

def test_connection():
	print("----- Starting System Verification -----")
	try:
		result=agent.run_sync("System check: Are you ready to conquer the Data and ML Engineering world ?")
		print(f"Agent response: {result.data}")
		print("----- Connection Successfull! -----")

	except Exception as e:
		print(f"----- Connection failed! -----\nError: {e}")

if __name__ == "__main__":
	test_connection()
