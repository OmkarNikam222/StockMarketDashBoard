import pandas as pd
import re

# Load CSV FILE

url = "https://raw.githubusercontent.com/gchandra10/filestorage/refs/heads/main/stock_market.csv"
df = pd.read_csv(url)

print("Shape:", df.shape)
print(df.head())
print(df.info())

df.columns = [re.sub(r'\s+', '_', c.strip().lower()) for c in df.columns] #regex

df = df.replace(["", " ", "na", "n/a", "none", "null", "-", "<na>"], pd.NA)

# Trim and lowercase 

for col in df.select_dtypes(include="object"):
    df[col] = df[col].astype(str).str.strip().str.lower()

df = df.replace(["na", "nan", "none", "-", "<na>", "null"], pd.NA)

# Fix date format (convert to yyyy-MM-dd)

df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce').dt.strftime("%Y-%m-%d")

# Drop duplicates and invalid rows

df = df.drop_duplicates().dropna(subset=['trade_date', 'ticker'])  

# Convert numeric columns

numeric_cols = ['open_price', 'close_price', 'volume']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop rows missing numeric core fields 
df = df.dropna(subset=['open_price', 'close_price', 'volume'], how='all')

df.to_parquet("data/cleaned.parquet", index=False)
print(" Cleaned data saved to data/cleaned.parquet")
print(f" Final shape: {df.shape}")
print(f" Unique tickers: {df['ticker'].nunique()}")
