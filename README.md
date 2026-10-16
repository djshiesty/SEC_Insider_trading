# SEC_Insider_trading

SEC Insider Trading Tracker

Summary: Through SEC EDGAR Form 4 filings for publicly traded companies, the project parses data from all the trades or changes in beneficial ownership of a certain company executives ownership in a company, scanning through for potential possibilities of company insider trading. By running it with the S&P 500, we can find alpha through comparisions.

How it works
Pull filings: Type a ticker. The program pulls the company's last 50 Form 4 filings from SEC EDGAR using edgartools.
Filter: Keeps open-market purchases (P) and sales (S). Drops pre-scheduled 10b5-1 plan trades and tax-withholding sales, since neither is a real choice. Same-day trades by one insider are merged into one event.
Measure: Runs a market-model Regression event study using daily prices from Yahoo Finance, cached for a day in SPY_tracker.py.
Output: A table sorted by trade size, average edge for buys and sales, and a Plotly chart saved as TICKER_edge.html.
Method

Based on the market model in Lasse Heje Pedersen's Efficiently Inefficient:

Regress the stock's daily excess returns on SPY's over the 120 trading days before the trade to get alpha and beta.
Cumulative Abnormal Return AKA CAR: Over the 21 trading days after, sum actual return minus expected return.
Edge: CAR for buys, negative CAR for sales, so positive always means good timing (Buys and sales are averaged separately so they don't cancel out).
How to run
bash
pip install edgartools yfinance pandas numpy plotly
python form4data.py

Results:

I looked at 3 stocks: GME, where large CEO buys showed a +16.6% CAR; NMM, whose CEO buys almost weekly, showed −2.2%; BETA, where insiders traded through proxy Michael R. Stone, showed +17.5%. This matches research that routine insider buys carry little signal, while opportunistic and discreet ones do. With only a few stocks, these are examples, not proof.

What I learned:

I had never used a GOVERNMENT DATA API, parsed SEC filings, or run an event study. The biggest lesson for me was that raw data lies. Many "purchases" were IPO allocations, and most sales were tax bills or pre-set financial plans.

Limitations:
1. Only 50 filings per company.
2. Offering allocations still show up as purchases.
3. The 21-day window misses longer-term bets.
4. Changes from proposal

Improvements: Used edgartools instead of requests and ElementTree, upgraded to Pedersen's market model, and added sales with 10b5-1 and tax filtering.

AI was used for debugging and code review.
