import pandas as pd

#Load existing data
df=pd.read_csv('data/retail_store_sales.csv')

#Artificially inject drift: Multiply all prices by 3
df['Price Per Unit']= df['Price Per Unit'] * 3
df['Total Spent'] = df['Total Spent'] # 3

#Save as the active file
df.to_csv('data/retail_store_sales.csv', index=False)
print("Drifted data crated, data is now 3x the baseline.")


