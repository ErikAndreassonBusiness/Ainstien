import glob
import os

import pandas as pd
import yfinance as yf
import time
from datetime import date, timedelta
import datetime

from app import create_app
from app.server.database import db, Company, Annual_Report, Quarterly_Report, Fundamental, Metric


#
# --- Getters for each excel-page
# 

def get_report_val(df, attr_name, col_name): 
    # Exctract data from a report
    mask = df['Report'] == attr_name
    if mask.any():
        val = df.loc[mask, col_name].values[0]
        # Handle empty/NaN values in Excel cleanly
        if pd.notna(val): 
            return float(val)
        
        raise ValueError

def get_info_val(info_df, label_name):
        # Look for the row where column index 1 contains our label
        mask = info_df.iloc[:, 1].astype(str).str.strip() == label_name
        if mask.any():
            val = info_df.loc[mask, info_df.columns[2]].values[0]
            return str(val).strip() if pd.notna(val) else None
        raise ValueError

def get_max_avarage_future_prices(ticker_obj, date): 
    future_target_date = date + timedelta(days=90)

    fetch_start = future_target_date - timedelta(days=30)
    fetch_end = future_target_date + timedelta(days=30)

    prices = ticker_obj.history(start=fetch_start, end=fetch_end, interval="1d")

    if prices.empty or len(prices) < 30:
        raise ValueError(f"Abort! Not enough price history to calculate MA50 for {future_target_date}")

    ma30_series = prices['Close'].rolling(window=30).mean()
    ma30_value = ma30_series.iloc[-1]

    if pd.isna(ma30_value):
        raise ValueError(f"Abort! MA50 calculation resulted in NaN at {future_target_date}")

    return round(float(ma30_value), 2)


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
#
# --- Helper functions
#
def get_file_path_for_company(export_folder, all_files, company_name):
    file_path = None

    for f in all_files:
        if f.endswith(f"-{company_name}.xlsx"):
            file_path = os.path.join(export_folder, f)
            break

    if not file_path:
        raise FileNotFoundError(f"No Excel file found matching '-{company_name}.xlsx'")
    
    return file_path


    # --- Get company from Excel list ---
def get_stock_data_from_excel(file_path):
    return pd.read_excel(file_path, sheet_name=None)

def get_fundamental_data(df, col): 
    return {
        "revenue": get_report_val(df, 'Nettoomsättning', col),
        "ebitda": get_report_val(df, 'EBITDA', col),
        "ebit": get_report_val(df, 'Rörelseresultat', col),
        "net_income": get_report_val(df, 'Resultat Före Skatt', col),
        "total_assets": get_report_val(df, 'Summa Tillgångar', col),
        "total_equity": get_report_val(df, 'Summa Eget Kapital', col),
        "total_debt": get_report_val(df, 'Totala Skulder', col),
        "short_term_debt": get_report_val(df, 'Kortfristiga Skulder', col),
        "long_term_debt": get_report_val(df, 'Långfristiga Skulder', col),
        "current_assets": get_report_val(df, 'Summa Omsättningstillgångar', col),
        "cash": get_report_val(df, 'Kassa/Bank', col),
        "fixed_assets": get_report_val(df, 'Summa Anläggningstillgångar', col)
    }

def get_metric_data(df, fundamental_data, col, report_columns): 
    col_index = list(report_columns).index(col)
    prev_col = list(report_columns)[col_index - 1] if col_index > 0 else None

    prev_revenue = get_report_val(df, 'Nettoomsättning', prev_col) if prev_col else 0
    prev_net_income = get_report_val(df, 'Resultat Före Skatt', prev_col) if prev_col else 0

    # Store variables for visability
    net_debt = get_report_val(df, 'Nettoskuld', col)
    ebitda = fundamental_data["ebitda"]
    revenue = fundamental_data["revenue"]
    ebit = fundamental_data["ebit"]
    net_income = fundamental_data["net_income"]
    total_assets = fundamental_data["total_assets"]
    total_equity = fundamental_data["total_equity"]

    return {
        # Growth metrics
        "revenue_growth_percent": ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0,
        "profit_growth_percent": ((net_income - prev_net_income) / prev_net_income * 100) if prev_net_income > 0 else 0.0,

        # Liquidity metrics
        "quick_ratio_percent": (fundamental_data["current_assets"] / fundamental_data["short_term_debt"] * 100) if fundamental_data["short_term_debt"] > 0 else 0.0,
        "net_debt_ebitda_ratio": (net_debt / ebitda) if ebitda > 0 else 0.0,

        # Leverage metrics
        "equity_ratio_percent": (total_equity / total_assets * 100) if total_assets > 0 else 0.0,

        "roa": (net_income / total_assets) if total_assets > 0 else 0.0,
        "roe": (net_income / total_equity) if total_equity > 0 else 0.0,
        "roi": (net_income / total_assets) if total_assets > 0 else 0.0,  # Approximation based on total assets

        # Profitability margins
        "ebit_margin_percent": (ebit / revenue * 100) if revenue > 0 else 0.0,
        "profit_margin_percent": (net_income / revenue * 100) if revenue > 0 else 0.0
    }

# --- IMPORTANT! A yfinance function!
def get_shares_outstanding(ticker_obj, date): 
    bal = ticker_obj.balance_sheet
    shares = bal.loc['Ordinary Shares Number', date]

    if pd.isna(shares) or shares == 0: 
            raise ValueError("Abort!")
    else: 
        return round(shares/1_000_000) #Millions

#
# =========== Instances of Entities ===========
#
def instance_company_entity(info_df):
    new_company = Company(
        borsdata_id= get_info_val(info_df, 'Börsdata ID'), 
        name=get_info_val(info_df, 'Bolag'), 
        ticker=get_info_val(info_df, 'Ticker'), 
        sektor = get_info_val(info_df, 'Sektor'), 
        branch = get_info_val(info_df, 'Bransch'), 
        lista = get_info_val(info_df, 'Lista'), 
        land = get_info_val(info_df, 'Land'))

    db.session.add(new_company)
    return new_company


def instance_fundamental_entity(fundamental_data):
    return Fundamental(
        revenue=fundamental_data["revenue"],
        ebitda=fundamental_data["ebitda"],
        ebit=fundamental_data["ebit"],
        net_income=fundamental_data["net_income"],
        total_assets=fundamental_data["total_assets"],
        total_equity=fundamental_data["total_equity"],
        total_debt=fundamental_data["total_debt"],
        short_term_debt=fundamental_data["short_term_debt"],
        long_term_debt=fundamental_data["long_term_debt"],
        current_assets=fundamental_data["current_assets"],
        cash=fundamental_data["cash"],
        fixed_assets=fundamental_data["fixed_assets"],
    )


def instance_metric_entity(metric_data):
    return Metric(
        revenue_growth_percent=metric_data["revenue_growth_percent"],
        profit_growth_percent=metric_data["profit_growth_percent"],
        quick_ratio_percent=metric_data["quick_ratio_percent"],
        net_debt_ebitda_ratio=metric_data["net_debt_ebitda_ratio"],
        equity_ratio_percent=metric_data["equity_ratio_percent"],
        roa=metric_data["roa"],
        roe=metric_data["roe"],
        roi=metric_data["roi"],
        ebit_margin_percent=metric_data["ebit_margin_percent"],
        profit_margin_percent=metric_data["profit_margin_percent"]
    )


def instance_annual_report_entity(year, df, company_obj, fundamental_obj, metric_obj = None): 
    ticker_obj = yf.Ticker(company_obj.ticker)
    date = datetime.datetime(int(year), 2, 15) # datum: 15 feb. year

    if metric_obj is not None: 
        return Annual_Report(
            report_date = date, 
            share_outstanding = get_shares_outstanding( 
                ticker_obj= ticker_obj, 
                date= date), 

            current_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date),
            
            one_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=30)),

            two_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=60)),
            
            three_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=90)),

            max_average_future_price = get_max_avarage_future_prices(
                ticker_obj=ticker_obj, 
                date=date),

            company = company_obj,
            fundamental = fundamental_obj,
            metric = metric_obj,
        )

    else: 
        return Annual_Report(
            report_date = date, 
            share_outstanding = get_shares_outstanding( 
                ticker_obj= ticker_obj, 
                date= date), 

            current_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date),
            
            one_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=30)),

            two_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=60)),
            
            three_month_price = get_price_at_report_date(
                ticker_obj=ticker_obj, 
                date=date + timedelta(days=90)),

            max_average_future_price = get_max_avarage_future_prices(
                ticker_obj=ticker_obj, 
                date=date),

            company = company_obj,
            fundamental = fundamental_obj,
        )

#
# --- Main instancing method
# 
def instance_anual_data_entities(year_df, company_obj): 
    report_columns = [col for col in year_df.columns if str(col).strip().isdigit() and len(str(col).strip()) == 4] #get all valid reports
    report_columns.sort()

    if len(report_columns) < 5: #minimum of 5 years reports
        raise ValueError("Not enough reports in company")

    first_year = True
    for col in report_columns:
        fundamental_data = get_fundamental_data(year_df, col)
        new_fundamental = instance_fundamental_entity(fundamental_data)

        if not first_year: #skip metric report firtst
            metric_data = get_metric_data(year_df, fundamental_data, col, report_columns)
            new_metric = instance_metric_entity(year_df)
            new_annual_report = instance_annual_report_entity(col, year_df, company_obj,new_fundamental, new_metric)
        else: 
            new_annual_report = instance_annual_report_entity(col, year_df, company_obj, new_fundamental)
        
        db.session.add(new_fundamental)
        if not first_year: #skip metric report firtst
            db.session.add(new_metric)
        db.session.add(new_annual_report)

        first_year = False

def run_seeding_engine():
    export_folder = 'Borsdata - Export'

    # --- Get a list of stocks to seed in db ---
    allstocks_df = pd.read_csv(f'{export_folder}/Borsdata_2026-07-10.csv')
    col_to_keep = allstocks_df.columns.get_loc('Bolagsnamn')
    allstocks_df = allstocks_df.iloc[:, :col_to_keep + 1] #Contains Borsdata ID and company name

    # --- Iterate through each stock and seed the database ---
    all_files = os.listdir(export_folder)
    for row in allstocks_df.itertuples():
        try: 
            # --- Load Excel sheets ---
            file_path = get_file_path_for_company(export_folder, all_files, row.Bolagsnamn)
            excel_data = get_stock_data_from_excel(file_path)

            # Instance and add entities
            new_company = instance_company_entity(excel_data["Info"])
            instance_anual_data_entities(excel_data['Year'], new_company) # Report, fundamental and metrics
            #instance_anual_data_entities(excel_data['Quarter'], new_company) # Report, fundamental and metrics

            # --- Commit everything
            db.session.commit()
            print(f"Successfully seeded {row.Bolagsnamn} ({len(year_df)} annual, {len(quarter_df)} quarterly reports)")

        except Exception as e: 
            print(f"  Skipping {row.Bolagsnamn}: Error: {traceback.print_exc()}" )


def seed_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        run_seeding_engine()

if __name__ == "__main__":
    seed_db()