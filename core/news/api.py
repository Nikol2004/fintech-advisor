import os, datetime, requests, pandas as pd
from dotenv import load_dotenv
load_dotenv()

def fetch_alpha_vantage_news(ticker: str, limit: int = 30) -> pd.DataFrame:
    key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not key:
        raise ValueError("ALPHAVANTAGE_API_KEY not set in .env")
    url = "https://www.alphavantage.co/query"
    params = {"function": "NEWS_SENTIMENT", "tickers": ticker.upper(), "sort": "LATEST", "limit": limit, "apikey": key}
    r = requests.get(url, params=params, timeout=20)
    js = r.json()
    feed = js.get("feed")
    if not feed:
        msg = js.get("Note") or js.get("Information") or "No news returned."
        raise ValueError(f"Alpha Vantage: {msg}")
    rows = []
    for item in feed:
        rows.append({
            "source": "Alpha Vantage",
            "title": item.get("title"),
            "link": item.get("url"),
            "published": item.get("time_published"),
            "sentiment": item.get("overall_sentiment_score"),
        })
    return pd.DataFrame(rows)

def fetch_finnhub_company_news(ticker: str, days: int = 14, max_items: int = 30) -> pd.DataFrame:
    key = os.getenv("FINNHUB_API_KEY", "")
    if not key:
        raise ValueError("FINNHUB_API_KEY not set in .env")
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    url = "https://finnhub.io/api/v1/company-news"
    params = {"symbol": ticker.upper(), "from": start.isoformat(), "to": end.isoformat(), "token": key}
    r = requests.get(url, params=params, timeout=20)
    arr = r.json()
    if isinstance(arr, dict) and arr.get("error"):
        raise ValueError(f"Finnhub: {arr.get('error')}")
    rows = []
    for item in arr[:max_items]:
        rows.append({
            "source": "Finnhub",
            "title": item.get("headline"),
            "link": item.get("url"),
            "published": item.get("datetime"),
            "category": item.get("category"),
        })
    return pd.DataFrame(rows)
