from seed_db.seed_fundementals import *

def safe_div(numerator, denominator):
    """Prevents ZeroDivisionError and handles NaN."""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        raise ValueError
    return round((numerator / denominator),2)
    
# == Growth Getters ===

def get_revenue_growth(inc, date, prev_date):
    current = get_revenue(inc, date)
    previous = get_revenue(inc, prev_date)
    return safe_div((current - previous), previous) * 100

def get_profit_growth(inc, date, prev_date):
    current = get_net_income(inc, date)
    previous = get_net_income(inc, prev_date)
    return safe_div((current - previous), previous) * 100

# === Efficiency & Returns ===

def get_roa(inc, bal, date):
    net_income = get_net_income(inc, date)
    total_assets = get_total_assets(bal, date)
    return safe_div(net_income, total_assets) * 100

def get_roe(inc, bal, date):
    net_income = get_net_income(inc, date)
    equity = get_total_equity(bal, date)
    return safe_div(net_income, equity) * 100

def get_roi(inc, bal, date):
    ebit = get_ebit(inc, date)
    capital = get_total_equity(bal, date) + get_long_debt(bal, date)
    return safe_div(ebit, capital) * 100

# === Liquidity & Solvency ===

def get_quick_ratio(bal, date):
    current_assets = get_current_assets(bal, date)
    inventory = get_inventory(bal, date)
    current_liab = get_short_debt(bal, date) 
    return safe_div((current_assets - inventory), current_liab) * 100

def get_equity_ratio(bal, date):
    equity = get_total_equity(bal, date)
    total_assets = get_total_assets(bal, date)
    return safe_div(equity, total_assets) * 100

def get_net_debt_ebitda(inc, bal, date):
    total_debt = get_total_debt(bal, date)
    cash = get_cash(bal, date)
    ebitda = get_ebitda(inc, date)
    net_debt = total_debt - cash
    return safe_div(net_debt, ebitda)

# === Turnover ===

def get_asset_turnover(inc, bal, date):
    revenue = get_revenue(inc, date)
    total_assets = get_total_assets(bal, date)
    return safe_div(revenue, total_assets)

def get_inventory_turnover(inc, bal, date):
    revenue = get_revenue(inc, date)
    inventory = get_inventory(bal, date)
    return safe_div(revenue, inventory)

# --- Margins ---

# def get_gross_margin(inc, date):
#     gross_profit = get_attribute(inc, ['Gross Profit'], date, fail_soft=True)
#     revenue = get_revenue(inc, date)
#     return safe_div(gross_profit, revenue) * 100

def get_ebit_margin(inc, date):
    ebit = get_ebit(inc, date)
    revenue = get_revenue(inc, date)
    return safe_div(ebit, revenue) * 100

def get_profit_margin(inc, date):
    net_income = get_net_income(inc, date)
    revenue = get_revenue(inc, date)
    return safe_div(net_income, revenue) * 100