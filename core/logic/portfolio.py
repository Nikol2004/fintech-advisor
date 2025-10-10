import pandas as pd

def allocation_for_score(score: int) -> pd.DataFrame:
    # Example UCITS-friendly tickers are illustrative only
    if score < 35:
        rows = [
            {"Asset": "Global Equity (e.g., VWCE)", "Percent": 20},
            {"Asset": "Global Bonds (e.g., AGGH/EUNA)", "Percent": 60},
            {"Asset": "Cash / T-Bills (e.g., BIL/EU cash)", "Percent": 20},
        ]
    elif score < 70:
        rows = [
            {"Asset": "Global Equity (e.g., VWCE)", "Percent": 50},
            {"Asset": "AI/Tech Tilt (e.g., IUIT/NDX ETF)", "Percent": 10},
            {"Asset": "Global Bonds (e.g., AGGH/EUNA)", "Percent": 30},
            {"Asset": "Cash / T-Bills", "Percent": 10},
        ]
    else:
        rows = [
            {"Asset": "Global Equity (e.g., VWCE)", "Percent": 70},
            {"Asset": "AI/Tech Tilt (e.g., IUIT/NDX ETF)", "Percent": 15},
            {"Asset": "Global Bonds (e.g., AGGH/EUNA)", "Percent": 10},
            {"Asset": "Cash / T-Bills", "Percent": 5},
        ]
    return pd.DataFrame(rows)

def insights_for_label(label: str) -> list[str]:
    if label == "Conservative":
        return [
            "Prioritize stability and low drawdowns.",
            "Use broad bond exposure; keep a cash buffer.",
            "Smaller equity slice for long-term growth."
        ]
    if label == "Balanced":
        return [
            "Mix growth and stability; rebalance annually.",
            "Add a small theme tilt (e.g., AI/Tech).",
            "Diversify across regions and durations."
        ]
    return [
        "Maximize long-term equity growth; accept volatility.",
        "Keep a modest bond/cash ballast for liquidity.",
        "Use disciplined rebalancing to control risk."
    ]
