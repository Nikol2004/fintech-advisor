import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_prices(ticker: str, days: int = 120) -> pd.DataFrame:
    end = datetime.today()
    start = end - timedelta(days=days)
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        raise ValueError("No price data found. Try another ticker.")
    return data
