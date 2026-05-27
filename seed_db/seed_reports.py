from datetime import timedelta
import pandas as pd
import yfinance as yf

def get_shares_outstanding(bal, date): 
    shares = bal.loc['Ordinary Shares Number', date]

    if pd.isna(shares) or shares == 0: 
            raise ValueError("Abort!")
    else: 
        return shares

def get_price_at_report_date(ticker_obj, date): 
    end_date = date + timedelta(days=7) # handeling holidays

    report_date_prices = ticker_obj.history(
        start=date, 
        end=end_date, 
        interval="1d")
    
    if report_date_prices.empty:
        raise ValueError(f"No price data found for {ticker_obj.ticker} around {date}")

    price = report_date_prices['Close'].iloc[0]

    if pd.isna(price):
        raise ValueError(f"Price data is NaN for {ticker_obj.ticker}")
    else:
        return round(price, 2)


def get_max_avarage_future_prices(ticker_obj, date): 
    future_target_date = date + timedelta(days=90)

    fetch_start = future_target_date - timedelta(days=80)
    fetch_end = future_target_date + timedelta(days=7)

    prices = ticker_obj.history(start=fetch_start, end=fetch_end, interval="1d")

    if prices.empty or len(prices) < 50:
        raise ValueError(f"Abort! Not enough price history to calculate MA50 for {future_target_date}")

    ma50_series = prices['Close'].rolling(window=50).mean()
    ma50_value = ma50_series.iloc[-1]

    if pd.isna(ma50_value):
        raise ValueError(f"Abort! MA50 calculation resulted in NaN at {future_target_date}")

    return round(float(ma50_value), 2)
        