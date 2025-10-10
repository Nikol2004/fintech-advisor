import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from core.data.prices import get_prices
from core.news.rss import default_feeds, fetch_rss
from core.news.api import fetch_alpha_vantage_news, fetch_finnhub_company_news
from core.logic.risk import compute_risk
from core.logic.portfolio import allocation_for_score, insights_for_label

load_dotenv()
st.set_page_config(page_title="Micro-Investment Advisor (MVP)", layout="centered")

# ---------------- Sidebar navigation (MVP wizard)
st.sidebar.title("MVP Wizard")
step = st.sidebar.radio(
    "Go to:",
    ["👤 Login", "🧭 Risk profile", "💡 Insights", "📊 Mock portfolio", "📈 Prices", "🗞 News"],
    index=0
)

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "risk" not in st.session_state:
    st.session_state.risk = None
if "allocation" not in st.session_state:
    st.session_state.allocation = None

# ---------------- Steps
if step == "👤 Login":
    st.title("🐝 Micro-Investment Advisor (MVP)")
    st.header("Login (demo)")
    name = st.text_input("Your name", value=st.session_state.user or "")
    agree = st.checkbox("I understand this is a demo (no real investing).")
    if st.button("Start session"):
        if name and agree:
            st.session_state.user = name
            st.success(f"Welcome, {name}! Go to **Risk profile** in the sidebar.")
        else:
            st.warning("Please enter your name and accept the checkbox.")

elif step == "🧭 Risk profile":
    st.title("🧭 Risk profile")
    if not st.session_state.user:
        st.info("Please login first in the sidebar.")
    col1, col2 = st.columns(2)
    with col1:
        horizon = st.slider("Investment horizon (years)", 0, 30, 5)
        horizon_pts = min(10, round(horizon / 3))  # map 0..30 yrs -> 0..10
        drawdown = st.select_slider("Max drop you can tolerate", options=["5%", "10%", "20%", "30%+"], value="10%")
        drawdown_pts = {"5%": 2, "10%": 4, "20%": 7, "30%+": 10}[drawdown]
        experience = st.select_slider("Investing experience", options=["None","Basic","Intermediate","Advanced"], value="Basic")
        experience_pts = {"None": 1, "Basic": 3, "Intermediate": 7, "Advanced": 10}[experience]
    with col2:
        income = st.select_slider("Income stability", options=["Low","Medium","High"], value="Medium")
        income_pts = {"Low": 3, "Medium": 6, "High": 10}[income]
        goal = st.select_slider("Main goal", options=["Capital preservation","Balanced growth","Max growth"], value="Balanced growth")
        goal_pts = {"Capital preservation": 2, "Balanced growth": 6, "Max growth": 10}[goal]

    if st.button("Compute risk"):
        answers = {
            "horizon": horizon_pts,
            "drawdown": drawdown_pts,
            "experience": experience_pts,
            "income_stability": income_pts,
            "goal_focus": goal_pts,
        }
        rp = compute_risk(answers)
        st.session_state.risk = rp
        st.success(f"Risk score: **{rp.score}** → **{rp.label}**")
        st.caption(f"Answers (pts): {answers}")

elif step == "💡 Insights":
    st.title("💡 Insights")
    rp = st.session_state.risk
    if not rp:
        st.info("Please fill the risk profile first.")
    else:
        bullets = insights_for_label(rp.label)
        st.subheader(f"{rp.label} profile — what it means")
        for b in bullets:
            st.write(f"• {b}")
        st.info("Tip: You can refine this later with live sentiment from the News step.")

elif step == "📊 Mock portfolio":
    st.title("📊 Mock portfolio")
    rp = st.session_state.risk
    if not rp:
        st.info("Please fill the risk profile first.")
    else:
        alloc = allocation_for_score(rp.score)
        st.session_state.allocation = alloc
        st.dataframe(alloc, use_container_width=True)
        st.bar_chart(alloc.set_index("Asset"))

        export = {
            "user": st.session_state.user,
            "risk": {"score": rp.score, "label": rp.label, "answers": rp.answers},
            "allocation": alloc.to_dict(orient="records"),
        }
        st.download_button("Download plan (JSON)", data=json.dumps(export, indent=2),
                           file_name="mvp_plan.json", mime="application/json")

elif step == "📈 Prices":
    st.title("📈 Prices")
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

elif step == "🗞 News":
    st.title("🗞 News")
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
            def as_dt(x):
                for fmt in ("s", None):
                    try:
                        return pd.to_datetime(x, unit=fmt) if fmt == "s" else pd.to_datetime(x)
                    except Exception:
                        pass
                return x
            if "published" in news.columns:
                news["published"] = news["published"].map(as_dt)
            st.dataframe(news[["source", "published", "title", "link"]], use_container_width=True)
        else:
            st.info("No news returned yet.")
