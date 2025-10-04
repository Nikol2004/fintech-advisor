from typing import List, Optional
import feedparser
import pandas as pd

def default_feeds(ticker: Optional[str] = None) -> List[str]:
    feeds = [
        "https://news.google.com/rss/search?q=stock+market&hl=en-US&gl=US&ceid=US:en",
        "https://feeds.marketwatch.com/marketwatch/topstories",
    ]
    if ticker:
        feeds.append(f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en")
        feeds.append(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US")
    return feeds

def fetch_rss(feeds: List[str], query: Optional[str] = None, limit: int = 25) -> pd.DataFrame:
    rows = []
    for url in feeds:
        feed = feedparser.parse(url)
        src = feed.feed.get("title", url)
        for e in feed.entries[:limit]:
            title = getattr(e, "title", "")
            if query and query.lower() not in title.lower():
                continue
            rows.append({
                "source": src,
                "title": title,
                "link": getattr(e, "link", ""),
                "published": getattr(e, "published", ""),
            })
    return pd.DataFrame(rows)
