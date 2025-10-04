import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))source .venv/bin/activate
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from core.data.prices import get_prices
from core.news.rss import default_feeds, fetch_rss
from core.news.api import fetch_alpha_vantage_news, fetch_finnhub_company_news

load_dotenv()
st.set_page_config(page_title="Micro-Investment Advisor (MVP)", layout="centered")
st.title("🐝 Micro-Investment Advisor (MVP)")

tab_prices, tab_news = st.tabs(["📈 Prices", "🗞 News"])

with tab_prices:
    ticker = st.text_input("Enter a stock/ETF ticker:", "AAPL")
    days = st.slider("Days of history", 30, 365, 120)
    source = st.selectbox("Price source", ["yahoo", "alpha", "finnhub"])

    if st.button("Run analysis"):
        try:
            df = get_prices(ticker, days, source=source)
            st.line_chart(df["Close"])
            st.caption("Last 10 rows")
            st.dataframe(df.tail(10))
        except Exception as e:
            st.error(str(e))

with tab_news:
    news_ticker = st.text_input("Ticker for news", "AAPL", key="news_ticker")
    sources = st.multiselect(
        "News sources",
        ["RSS (Google/Yahoo)", "Alpha Vantage", "Finnhub"],
        default=["RSS (Google/Yahoo)"]
    )
    if st.button("Fetch news"):
        frames = []
        if "RSS (Google/Yahoo)" in sources:
            rss_df = fetch_rss(default_feeds(news_ticker), limit=15)
            frames.append(rss_df)
        if "Alpha Vantage" in sources:
            try:
                frames.append(fetch_alpha_vantage_news(news_ticker, limit=20))
            except Exception as e:
                st.warning(f"Alpha Vantage: {e}")
        if "Finnhub" in sources:
            try:
                frames.append(fetch_finnhub_company_news(news_ticker, days=14, max_items=20))
            except Exception as e:
                st.warning(f"Finnhub: {e}")

        if frames:
            news = pd.concat(frames, ignore_index=True)
            # make 'published' readable where possible
            def as_dt(x):
                for fmt in ("s", None):
                    try:
                        return pd.to_datetime(x, unit=fmt) if fmt == "s" else pd.to_datetime(x)
                    except Exception:
                        pass
                return x
            if "published" in news.columns:
                news["published"] = news["published"].map(as_dt)
            st.dataframe(news[["source", "published", "title", "link"]])
        else:
            st.info("No news returned yet.")
