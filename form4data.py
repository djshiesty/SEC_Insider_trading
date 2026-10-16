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
            if df.empty:
                continue
            try:
                xml = filing.xml() or ""
            except Exception:
                xml = ""
            low = xml.lower()
            df["Plan"] = "<aff10b5one>1" in low or "<aff10b5one>true" in low or "10b5-1" in low
            df["Tax"] = any(w in low for w in ["tax withholding", "tax liabilit", "tax obligation", "sell to cover", "sell-to-cover"])
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
            trades = df[df["Code"].isin(["P", "S"]) & ~df["Plan"] & ~df["Tax"]]
            if trades.empty:
                print("No discretionary insider buys or sales.")
                continue
            trades = trades.groupby(["Date", "Insider", "Code"], as_index=False)["Value"].sum()
            trades = trades.sort_values("Value", ascending=False)
            trades["CAR"] = pd.to_numeric(
                [cumulative_abnormal_return(ticker, pd.to_datetime(d)) for d in trades["Date"]],
                errors="coerce")
            trades["Edge"] = trades["CAR"].where(trades["Code"] == "P", -trades["CAR"])
            print(trades[["Date", "Insider", "Code", "Value", "CAR", "Edge"]])
            print(trades.groupby("Code")["Edge"].mean().rename({"P": "Avg buy edge", "S": "Avg sale edge"})) #AI Helped with print statements
            print(f"Overall edge: {trades['Edge'].mean():.2%}") 
            fig = px.bar(trades, x="Date", y="Edge", color="Code", hover_data=["Insider", "Value", "CAR"],
                         title=f"{ticker}: insider timing edge over 21 trading days (P = buy, S = sale)")
            fig.write_html(f"{ticker}_edge.html")
            print(f"Chart saved to {ticker}_edge.html")
            print(f"Chart saved to {ticker}_car.html")
        except Exception:
            print(f"Could not find ticker: {ticker}. Try again.")
    
'''

FYI: Caller needed a lot of help from AI to understand the logic and how I can
categorize the data for all trades that are both Buy AND Sell by insider. I
learned a lot from understanding how I can use specific methods to manipulate
and edit dataframes. Additionally debugged and reviewed using AI, did not
artificially generate entire script or core logic. 

'''

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
