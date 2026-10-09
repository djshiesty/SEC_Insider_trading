import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from time import time

# Calculate dates based on today's date

BENCHMARK = "SPY"

_cache = {}
CACHE_TTL = 60*60*24

def get_price_data(ticker, start):
    """
    Fetch historical price data for a given ticker and date range.
    
    Parameters:
    ticker (str): Stock ticker symbol (e.g., 'AAPL')
    start_date (str): Start date in 'YYYY-MM-DD' format
    end_date (str): End date in 'YYYY-MM-DD' format
    
    Returns:
    pd.DataFrame: DataFrame containing historical price data
    """
    today = datetime.now()
    start_date = today - timedelta(days = start)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = today.strftime('%Y-%m-%d')
    
    data = yf.download(ticker, start = start_str, end = end_str, auto_adjust=True)
    if data is None or data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data.dropna()

def get_cached_data(ticker, start):
    '''
    Caching data is important in this context because fetching historical price data from an external source 
    like Yahoo Finance is time-consuming and involves rate limits in calling. 
    By caching the data, we can avoid unnecessary API calls and improve the performance of our application. 
   
    The cache is set to expire after a certain time of 60 days, ensuring that we get reasonably up-to-date data
    without overwhelming the data source with requests.
    '''
    key=(ticker,start)
    if key not in _cache or time() - _cache[key]["timestamp"] > CACHE_TTL:
        _cache[key] = {"data": get_price_data(ticker, start), "timestamp": time()}
    return _cache[key]["data"]