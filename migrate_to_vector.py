import chromadb
from chromadb.utils import embedding_functions
import json
import os

#1. Setup Persistent Storage on local machine
client = chromadb.PersistentClient(path="./chroma_db")

#2. Use a standard embedding model ( runs locally on machine )
default_ef = embedding_functions.DefaultEmbeddingFunction()

#3. Create ( or get ) the collection
collection = client.get_or_create_collection(
	name = "transformation_recipes",
	embedding_function = default_ef
)

#4. Load existing JSON recipes
with open('memory_store.json', 'r') as f:
	recipes_data = json.load(f)

#5. Ingest into vector DB.( Handling both list and dict. )
if isinstance(recipes_data, dict):
	recipes_list = recipes_data.get('recipes', [])
else:
	recipes_list = recipes_data.get('recipes', [])

for i, recipe in enumerate(recipes_list):
	#Combine the issue and explanation for better semantic search.
	combined_text = f"{recipe['issue']}: {recipe['explanation']}"

	collection.add(
		documents = [combined_text],
		metadatas = [{"solution":recipe['solution'], "issue":recipe['issue'], "keyword":recipe.get('keyword', '')}],
		ids = [f"id_{i}"]
	)

print(f"Successfully migrated {len(recipes_list)} recipes to ChromaDB!")

# Quick Test: Searching for 'precision'
results = collection.query(
    query_texts=["How to fix decimals?"],
    n_results=1
)
print("\n--- TEST SEARCH RESULT ---")
print(f"Found Issue: {results['metadatas'][0][0]['issue']}")
print(f"Suggested Code: {results['metadatas'][0][0]['solution']}")
