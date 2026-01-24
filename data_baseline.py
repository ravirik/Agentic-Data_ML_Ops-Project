import pandas as pd
import json

# Load the original data
df = pd.read_csv('data/retail_store_sales.csv')

# Generate a statistical fingerprint
baseline = {
	"Price Per Unit": {"mean": df['Price Per Unit'].mean(), "std": df['Price Per Unit'].std()},
	"Total Spent": {"mean": df['Total Spent'].mean(), "std": df['Total Spent'].std()},
	"Quantity": {"mean": df['Quantity'].mean(), "std": df['Quantity'].std()}
}

with open ('baseline_stats.json', 'w') as f:
	json.dump(baseline, f)
print('Baseline stats generated')
