import pandas as pd

df=pd.read_csv('data/retail_store_sales.csv')
df['Price Per Unit'] = df['Price Per Unit'] / 3
df['Total Spent'] = df['Total Spent'] / 3

df.to_csv('data/retail_store_sales.csv', index=False)
print('Data restored to original values')

