
import pandas as pd
from datetime import datetime
from .events import MarketDataEvent


# load the csv file 
data = pd.read_csv("sample_prices.csv")

for index, row in data.iterrows():
    print(row)

"""
Each row is like this: 

{
  "timestamp": "2026-01-01",
  "symbol": "AAPL",
  "open": 100,
  "high": 105,
  "low": 99,S
  "close": 103,
  "volume": 10000
}

"""

# Acess values
for _, row in data.iterrows():
    event = MarketDataEvent(
        symbol=row["symbol"],
        timestamp=row["timestamp"],
        open=row["open"],
        high=row["high"],
        low=row["low"],
        close=row["close"],
        volume=row["volume"]
    )
    print(event)