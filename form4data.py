import pandas as pd

from edgar import set_identity, Company
from datetime import datetime
from spy_tracker import get_cached_data, BENCHMARK

set_identity("Your Name your.email@example.com")
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
            print(df.columns)
            print(df.head() if not df.empty else "No insider trades found.")
        except Exception as e:
            print(f"Could not find ticker: {ticker}. Try again.")


def excess_returns(ticker, buys, days=21):
    """Stock return minus SPY return over ~30 days (21 trading days) after each insider buy."""
    dates = pd.to_datetime(buys["Date"])
    daysbf = (datetime.now() - dates.min()).days + 5
    stock = get_cached_data(ticker, daysbf)["Close"]
    spy = get_cached_data(BENCHMARK, daysbf)["Close"]

    results = []
    for date in dates:
        s = stock[stock.index >= date].iloc[:days + 1]
        b = spy[spy.index >= date].iloc[:days + 1]
        if len(s) < days + 1:  # not 30 days since the buy yet
            results.append(None)
        else:
            results.append((s.iloc[-1] / s.iloc[0] - 1) - (b.iloc[-1] / b.iloc[0] - 1))
    buys = buys.copy()
    buys["Excess Return"] = results
    return buys

def market_model():
    pass

if __name__ == "__main__":
    caller()