import yfinance as yf
import pandas as pd

# Constants
REVENUE_LIST = ['Total Revenue', 'Revenue', 'Operating Revenue']

def get_inc_attribute(inc, key_list, report_date): 
    for key in key_list:
        if key in inc.index:
            attribute = inc.loc[key, report_date]
            if pd.notna(attribute) and attribute != 0:
                return attribute
    
    raise ValueError(f"Attributes {key_list} not found or zero for {report_date}")


# ========== Calculate Margins ==========
def calc_gross_profit_margin(inc, report_date):
    gross_profit_list = ['Gross Profit', 'GrossProfit']

    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    gross_profit = get_inc_attribute(inc, gross_profit_list, report_date)

    return round(100 * (gross_profit / revenue), 2)

def calc_operating_margin(inc, report_date):
    operating_income_list = ['EBIT']

    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    operating_income = get_inc_attribute(inc, operating_income_list, report_date)

    return round(100 * (operating_income / revenue), 2)

def calc_operating_margin(inc, report_date):
    operating_income_list = ['Net Income']

    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    operating_income = get_inc_attribute(inc, operating_income_list, report_date)

    return round(100 * (operating_income / revenue), 2)

# ========= Calculate Growth ===========
def calc_growth(current, previous):
    return round(100 * ((current - previous) / previous), 2)

# ======== Calculare Liquidy Ratios =======
def calc_quick_ratio(current_assets, inventory, wip, short_term_debt): 
    return round((current_assets - inventory - wip) / short_term_debt, 2)

def calc_net_debt_ebitda(net_debt, ebitda):
    return round(net_debt / ebitda, 2)

def calc_equity_ratio(total_equity, total_assets):
    return round(total_equity / total_assets, 2)