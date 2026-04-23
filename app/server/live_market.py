import yfinance as yf
import datetime

def get_yf_stock(ticker): 
    return yf.Ticker(ticker)

def get_stock_description(stock_obj): 
    return stock_obj.info.get('shortBusinessSummary', 'Description currently unavailable.')

def get_stock_sector(stock_obj): 
    return stock_obj.info.get('sector', 'N/A')

def get_stock_industry(stock_obj): 
    return stock_obj.info.get('industry', 'N/A')

def get_current_price(stock_obj): 
    return stock_obj.info.get('currentPrice')

def get_price_history(stock_obj, period="1y"): 
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)
    df = stock_obj.history(
        start=start_date, 
        end=end_date, 
        interval="1d", 
        auto_adjust=True) #adjust for stock splits etc.

    if df.empty:
        # Debug print in your terminal so you can see if it's failing
        print(f"DEBUG: No history found for ticker.")
        return {"dates": [], "prices": []}

    return {
        "dates": df.index.strftime('%Y-%m-%d').tolist(),
        "prices": df['Close'].tolist()
    }

def get_live_market_data(ticker):
    """
    Consolidates all real-time data fetching into a single call.
    Returns a dictionary with description, price, and history.
    """
    stock = get_yf_stock(ticker)
    
    # Fetch history first (often the slowest part)
    sector = get_stock_sector(stock)      
    industry = get_stock_industry(stock) 
    history = get_price_history(stock)
    
    return {
        "category_info": f"{sector} | {industry}", #display sector and industyr
        "current_price": get_current_price(stock),
        "history_dates": history['dates'],
        "history_prices": history['prices']
    }