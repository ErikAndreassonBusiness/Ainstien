import pandas as pd

def get_attribute(sheet, key_list, report_date): 
    for key in key_list:
        if key in sheet.index:
            attribute = sheet.loc[key, report_date]
            if pd.notna(attribute) and attribute != 0:
                return round(attribute / 1_000_000, 0) #MSEK
    
    print("Cannot find: ", key_list[0])
    raise ValueError(f"Attributes {key_list} not found or zero for {report_date}")

# ===== Income Statement Getters =====
def get_revenue(inc, report_date): 
    keys = ['Total Revenue', 'Operating Revenue', 'Revenue', 'Net Sales']
    return get_attribute(inc, keys, report_date)

def get_ebitda(inc, report_date):
    keys = ['EBITDA', 'Normalized EBITDA']
    return get_attribute(inc, keys, report_date)

def get_ebit(inc, report_date):
    keys = ['EBIT', 'Operating Income', 'Operating Profit']
    return get_attribute(inc, keys, report_date)

def get_net_income(inc, report_date):
    keys = ['Net Income', 'Net Income Common Stockholders', 'Net Income From Continuing Operation']
    return get_attribute(inc, keys, report_date)

def get_depreciation(inc, report_date):
    # This is often hidden in 'Reconciled Depreciation' in yfinance
    keys = ['Reconciled Depreciation', 'Depreciation And Amortization', 'Depreciation']
    return get_attribute(inc, keys, report_date)


# ===== Balance Sheet Getters =====
def get_substansvarde(bal, report_date): 
    intangibles_keys = ['Goodwill And Other Intangible Assets', 'Goodwill', 'Intangible Assets']
    intangibles = get_attribute(bal, intangibles_keys, report_date)

    substansvarde =  get_total_equity(bal, report_date) - intangibles
    return max(0, substansvarde)

def get_total_assets(bal, report_date):
    keys = ['Total Assets']
    return get_attribute(bal, keys, report_date)

def get_total_equity(bal, report_date):
    keys = ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity']
    return get_attribute(bal, keys, report_date)

def get_total_debt(bal, report_date):
    keys = ['Total Debt', 'Total Liabilities Net Minority Interest'] 
    return get_attribute(bal, keys, report_date)

def get_short_debt(bal, report_date):
    keys = ['Current Debt', 'Short Long Term Debt', 'Current Liabilities']
    return get_attribute(bal, keys, report_date)

def get_long_debt(bal, report_date):
    return get_total_debt(bal, report_date) - get_short_debt(bal, report_date)

def get_current_assets(bal, report_date):
    keys = ['Total Current Assets', 'Current Assets']
    return get_attribute(bal, keys, report_date)

def get_inventory(bal, report_date):
    keys = ['Inventory', 'Inventories']
    return get_attribute(bal, keys, report_date)

def get_receivables(bal, report_date):
    keys = ['Receivables', 'Accounts Receivable', 'Net Receivables']
    return get_attribute(bal, keys, report_date)

def get_cash(bal, report_date):
    keys = ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments', 'Cash']
    return get_attribute(bal, keys, report_date)

def get_fixed_assets(bal, report_date):
    keys = ['Net PPE', 'Properties', 'Fixed Assets']
    return get_attribute(bal, keys, report_date)

def get_goodwill(bal, report_date):
    keys = ['Goodwill', 'Goodwill And Other Intangible Assets']
    return get_attribute(bal, keys, report_date)