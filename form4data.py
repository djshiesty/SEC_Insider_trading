import pandas as pd
import numpy as np
from edgar import set_identity, Company
from datetime import datetime
from SPY_tracker import get_cached_data, BENCHMARK
import plotly.express as px

set_identity("Atharva soni20283106@student.nhvweb.net")
def analyze(ticker):
    
    company = Company(ticker)
    filings = company.get_filings(form="4").head(50)
    frames = []
    
    for filing in filings:
        try:
            df = filing.obj().to_dataframe()
            if not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"Skipped {filing.accession_no}: {e}")
    
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame() # AI Helped out with the "ignire_index = True"

def caller():
    while True:
        ticker = input("Ticker (or 'q' to quit): ").upper()
        if ticker == "Q":
            break
        try:
            df = analyze(ticker)
            if df.empty:
                print("No insider trades found.")
                continue
            buys = df[df["Code"] == "P"]
            if buys.empty:
                print("No open-market insider buys.")
                continue
            else:
                buys = buys.copy()
                buys["CAR"] = [cumulative_abnormal_return(ticker, pd.to_datetime(d)) for d in buys["Date"]]
                print(buys[["Date", "Insider", "Value", "CAR"]])
                print(f"Average CAR: {buys['CAR'].mean():.2%}")
                fig = px.bar(buys, x="Date", y="CAR", hover_data=["Insider", "Value"],
                         title=f"{ticker}: 30-day abnormal return after insider buys")
                fig.show()
        except Exception:
            print(f"Could not find ticker: {ticker}. Try again.")
    

def market_model(stock, SPY):
    beta, alpha = np.polyfit(SPY,stock,1)
    return alpha, beta

def cumulative_abnormal_return(ticker, buydate):
    daysbf = 730
    riskfree = get_cached_data("^IRX", daysbf)["Close"] / 100 / 252
    data = pd.DataFrame({
        "stock": get_cached_data(ticker, daysbf)["Close"].pct_change() - riskfree,
        "spy": get_cached_data(BENCHMARK, daysbf)["Close"].pct_change() - riskfree,
    }).dropna()

    before = data[data.index < buydate].tail(120)
    after = data[data.index >= buydate].head(21)
    if len(before) < 120 or len(after) < 21:
        return None

    alpha, beta = market_model(before["stock"], before["spy"])
    return (after["stock"] - alpha - beta * after["spy"]).sum()

if __name__ == "__main__":
    caller()
