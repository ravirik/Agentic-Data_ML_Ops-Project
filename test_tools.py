import json
import pandas as pd
from reasoning import inspect_dataset, search_knowledge_store, apply_transformation

def pre_flight_check():
	print("--- STARTING LOCAL PRE-FLIGHT CHECK ---")

	# 1. Test JSON Memory store
	try:
		with open('memory_store.json', 'r') as f:
			data = json.load(f)
			print (f" JSON valid. Found {len(data['recipes'])} recipes.")
	except Exception as e:
		print (f"JSON ERROR: {e}")

	#2. Test inspect_dataset tool
	try:
		# We pass None as 'ctx' because we aren't using agent state yet
		data_info = inspect_dataset(None)
		print (f" Data Inspection Tool working.")
	except Exception as e:
		print (f" INSPECT TOOL ERROR: {e}")

	#3. Test search_knowledge_store Tool
	try:
		result = search_knowledge_store(None, search_term ="Precision")
		print(f"DEBUG SERACH RESULT : {result}")
	except Exception as e:
		print (f" MEMORY TOOL ERROR: {e}")
	
	#4. Test apply_transformation tool
	try:
		# Mocking the call agent will make
		test_code = "df[col] = df[col].round(2)"
		res = apply_transformation(None, column_name = 'Price Per Unit', python_code = test_code)
		if "SUCCESS" in res:
			print (f" Executioner Tool working")
		else:
			print (f" Executioner tool failed: {res}")
	except Exception as e:
		print (f" EXECUTIONER ERROR: {e}")

if __name__ == "__main__":
	pre_flight_check() 
