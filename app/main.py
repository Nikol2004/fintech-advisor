import streamlit as st
from core.data.prices import get_prices

st.title("💸 Micro-Investment Advisor (MVP)")

ticker = st.text_input("Enter a stock/ETF ticker:", "AAPL")
days = st.slider("Days of history", 30, 365, 120)

if st.button("Run analysis"):
    df = get_prices(ticker, days)
    st.line_chart(df["Close"])
