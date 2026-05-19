import pandas as pd

# Constants
REVENUE_LIST = ['Total Revenue', 'Revenue', 'Operating Revenue']
GROSS_PROFIT_LIST = ['Gross Profit', 'GrossProfit']
OPERATING_INCOME_LIST = ['EBIT', 'Operating Income']
NET_INCOME_LIST = ['Net Income']

def get_inc_attribute(inc, key_list, report_date): 
    for key in key_list:
        if key in inc.index:
            attribute = inc.loc[key, report_date]
            if pd.notna(attribute) and attribute != 0:
                return attribute
    
    raise ValueError(f"Attributes {key_list} not found or zero for {report_date}")


# ======= Calculate Profitablility Ratios ======
def calc_gross_profit_margin(inc, report_date):
    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    gross_profit = get_inc_attribute(inc, GROSS_PROFIT_LIST, report_date)

    return round(100 * (gross_profit / revenue), 2)

def calc_operating_margin(inc, report_date):
    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    operating_income = get_inc_attribute(inc, OPERATING_INCOME_LIST, report_date)

    return round(100 * (operating_income / revenue), 2)

def calc_profit_margin(inc, report_date):
    revenue = get_inc_attribute(inc, REVENUE_LIST, report_date)
    net_income = get_inc_attribute(inc, NET_INCOME_LIST, report_date)

    return round(100 * (net_income / revenue), 2)

# ========= Calculate Growth ===========
def calc_growth(current, previous):
    return round(100 * ((current - previous) / previous), 2)

# ======== Calculare Liquidy Ratios =======
def calc_current_assets(bal, prev_bal): 
    return 

def calc_quick_ratio(current_assets, inventory, wip, short_term_debt): #%
    return round((current_assets - inventory - wip) / short_term_debt, 2) * 100

def calc_net_debt_ebitda(net_debt, ebitda): #ggr
    return round(net_debt / ebitda, 2)

def calc_equity_ratio(total_equity, total_average_assets): #%
    return round(total_equity / total_assets, 2) * 100

# ======= Calculate Efficiancy Ratios ======
def calc_turnover_ratio(sales, total_average_assets): #ggr
    return round(sales / total_average_assets, 2)

def calc_inventory_turnover_ratio(cost_of_goods_sold, average_inventory): #ggr
    return round(cost_of_goods_sold / average_inventory, 2)

def calc_ROA(net_income, total_average_assets): #%
    return round(net_income / total_average_assets, 2) * 100

def calc_ROE(net_income, average_shareholders_equity): #%
    return round(net_income / average_shareholders_equity, 2) * 100

def calc_ROI(net_income, cost_of_investment): #%
    return round(net_income / cost_of_investment, 2) * 100