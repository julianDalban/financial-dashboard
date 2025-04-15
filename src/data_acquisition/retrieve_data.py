import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def get_stock_data(ticker_symbol: str, period: str='1y', interval: str='1d') -> Optional[pd.DataFrame]:
    '''
    Retrieves historical data for a particular stock from Yahoo Finance.
    
    Params:
    ticker_symbol: stock symbol to retrieve
    period: Time period to retrieve (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
    Dataframe: Historical stock data
    '''
    try:
        ticker = yf.Ticker(ticker_symbol)

        df = ticker.history(period=period, interval=interval)
        
        df = df.reset_index()
        
        if df.empty:
            print(f'No data found for {ticker_symbol}')
            return None
        
        return df
    except Exception as e:
        print(f'Error retrieving data for {ticker_symbol}: {e}')
        return None

def process_time_series(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    '''
    Process time series data for analysis.
    
    Params:
    df: Raw stock data Dataframe
    
    Returns:
    DataFrame: Process Dataframe
    '''
    if df is None or df.empty:
        return None
    
    processed_df = df.copy()
    
    if 'Date' in processed_df.columns:
        processed_df['Date'] = pd.to_datetime(processed_df['Date']) # convert timestamp to pd Datetime object
    
    processed_df = processed_df.set_index('Date') # set Date as index for time series operations, allows useful datetime attributes
    
    processed_df = processed_df.ffill() # fill missing values using forward fill 
    
    processed_df['DayOfWeek'] = processed_df.index.dayofweek # datetime attribute
    processed_df['Month'] = processed_df.index.month # datetime attribute
    
    return processed_df

def calculate_basic_metrics(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    '''
    Calculates basic metrics and adds their values to the df.
    
    Params:
    df: Process stock data Dataframe
    
    Returns:
    Dataframe: Dataframe with added metrics
    '''
    if df is None or df.empty:
        return None
    
    metrics_df = df.copy()
    
    metrics_df['Daily_Return'] = metrics_df['Close'].pct_change() * 100 # daily return
    
    # calculating cumulative returns based on first day of dataset
    metrics_df['Cum_Return'] = (1 + metrics_df['Daily_Return']/100).cumprod() - 1
    metrics_df['Cum_Return'] = metrics_df['Cum_Return'] * 100 # to pct
    
    # determine volatility (20-day rolling standard deviation of returns), can be added as param in future
    metrics_df['Volatility_20d'] = metrics_df['Daily_Return'].rolling(window=20).std() # rolling uses sliding window approach
    
    # volume changes, volume is total number of shares traded during the day (buy and sell)
    metrics_df['Volume_Change'] = metrics_df['Volume'].pct_change() * 100
    
    # Moving averages for closing prices (5-day, 20-day, and 50-day)
    metrics_df['5d_MA'] = metrics_df['Close'].rolling(window=5).mean()
    metrics_df['20d_MA'] = metrics_df['Close'].rolling(window=20).mean()
    metrics_df['50d_MA'] = metrics_df['Close'].rolling(window=50).mean()
    
    return metrics_df