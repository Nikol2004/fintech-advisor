import os
from datetime import datetime, timedelta
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# ---------- Yahoo (yfinance)
def _prices_yahoo(ticker: str, days: int = 120) -> pd.DataFrame:
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=days)
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        raise ValueError("No price data from Yahoo Finance.")
    return df

# ---------- Alpha Vantage (daily adjusted)
def _prices_alpha_vantage(ticker: str, days: int = 120) -> pd.DataFrame:
    key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not key:
        raise ValueError("ALPHAVANTAGE_API_KEY not set in .env")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker.upper(),
        "outputsize": "full" if days > 100 else "compact",
        "datatype": "json",
        "apikey": key,
    }
    r = requests.get(url, params=params, timeout=20)
    js = r.json()
    ts = js.get("Time Series (Daily)")
    if not ts:
        msg = js.get("Note") or js.get("Information") or "No data returned."
        raise ValueError(f"Alpha Vantage: {msg}")

    rows = []
    for d, v in ts.items():
        rows.append({
            "Date": pd.to_datetime(d),
            "Open": float(v["1. open"]),
            "High": float(v["2. high"]),
            "Low": float(v["3. low"]),
            "Close": float(v["4. close"]),
            "Adj Close": float(v["5. adjusted close"]),
            "Volume": int(v["6. volume"]),
        })
    df = pd.DataFrame(rows).sort_values("Date")
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=days + 2)
    df = df[df["Date"] >= cutoff].set_index("Date")
    return df

# ---------- Finnhub (daily candles)
def _prices_finnhub(ticker: str, days: int = 120) -> pd.DataFrame:
    key = os.getenv("FINNHUB_API_KEY", "")
    if not key:
        raise ValueError("FINNHUB_API_KEY not set in .env")
    now = pd.Timestamp.now()
    fro = int((now - pd.Timedelta(days=days)).timestamp())
    to = int(now.timestamp())
    url = "https://finnhub.io/api/v1/stock/candle"
    params = {"symbol": ticker.upper(), "resolution": "D", "from": fro, "to": to, "token": key}
    r = requests.get(url, params=params, timeout=20)
    js = r.json()
    if js.get("s") != "ok":
        raise ValueError(f"Finnhub: {js.get('s')}")
    df = pd.DataFrame({
        "Date": pd.to_datetime(js["t"], unit="s"),
        "Open": js["o"], "High": js["h"], "Low": js["l"], "Close": js["c"], "Volume": js["v"]
    }).set_index("Date")
    return df

# ---------- Public entry
def get_prices(ticker: str, days: int = 120, source: str = "yahoo") -> pd.DataFrame:
    source = source.lower()
    if source == "alpha":
        return _prices_alpha_vantage(ticker, days)
    if source == "finnhub":
        return _prices_finnhub(ticker, days)
    return _prices_yahoo(ticker, days)
