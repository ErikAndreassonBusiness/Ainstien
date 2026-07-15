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
# ========== Getters and helper function ==========
# 
import re
import pandas as pd


def get_shares_outstading_dict(df):
    result = {}

    values = df["Börsvärde"].astype(str).str.strip().tolist()
    quarter_pattern = re.compile(r"Q[1-4]\s+\d{4}")

    for i in range(len(values)):
        if quarter_pattern.match(values[i]):
            quarter = values[i]

            if i + 2 < len(values):
                shares_str = (
                    values[i + 2].replace(",", ".").replace(" ", "").strip()
                )
                try:
                    shares = float(shares_str)
                    if shares.is_integer():
                        shares = int(shares)
                except ValueError:
                    shares = shares_str

                result[quarter] = shares

    return result

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


def get_shares_outstanding(ticker, date):
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.balance_sheet
        
    shares_row = df.loc['Ordinary Shares Number']
    shares_row.index = pd.to_datetime(shares_row.index)
    
    # Get valid dates
    target_date = pd.to_datetime(date)
    valid_shares = shares_row[shares_row.index <= target_date]
    
    if valid_shares.empty:
        # If target date is past the oldest record, get the oldest
        closest_date = shares_row.index.min()
    else:
        # Grab the closest date
        closest_date = valid_shares.index.max()
        
    shares_val = shares_row[closest_date]
    
    if pd.isna(shares_val) or shares_val == 0:
        print(f"No valid shares found on or near {target_date.strftime('%Y-%m-%d')}.")
        raise ValueError("  No valid amount of shares outstanding found")
        
    print(f"Target Date: {target_date.strftime('%Y-%m-%d')} | Closest Report Date: {closest_date.strftime('%Y-%m-%d')}")
    print(f"Shares outstanding: {shares_val}")
    
    return int(shares_val) 


def get_max_average_future_prices(price_df, date):
    fetch_end = (date + timedelta(days=90 + 15)).strftime('%Y-%m-%d')

    window_df = price_df[price_df['Date'] <= fetch_end].copy()
    window_df.dropna(subset=['Closeprice'], inplace=True) #No NaN's
    window_df.sort_values('Date', ascending=True, inplace=True)
    
    # Calc MA30 average max value
    window_df['ma30'] = window_df['Closeprice'].rolling(window=30, min_periods=1).mean()
    ma30_value = window_df['ma30'].max()

    return round(float(ma30_value), 2)

def get_price_at_report_date(price_df, date):
    date_str = date.strftime('%Y-%m-%d')
    max_data_date_str = price_df['Date'].max()
    min_data_date_str = price_df['Date'].min()
    
    if date_str > max_data_date_str:
        return price_df.loc[price_df['Date'] == max_data_date_str, 'Closeprice'].values[0]
        
    # If the report date is somehow older than your data history limits
    if date_str < min_data_date_str:
        print(f"    !!!Warning, not enough price data, use yfinance instead!!!")
        return price_df.loc[price_df['Date'] == min_data_date_str, 'Closeprice'].values[0]

    matching_rows = price_df.loc[price_df['Date'] == date_str, 'Closeprice']
    
    # 4. If matching_rows is NOT empty, we safely return the price
    if not matching_rows.empty:
        return matching_rows.values[0]
    else:
        # weekend or holiday)
        return get_price_at_report_date(price_df, date + timedelta(days=1))


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
    if get_report_val(df, 'Summa Eget Kapital', col) < 0: 
        raise ValueError("  Total Equity is < 0!")

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

#
# =========== Instances of Entities ===========
#
def instance_company_entity(info_df):
    ticker = get_info_val(info_df, 'Ticker')
    new_company = Company(
        name=get_info_val(info_df, 'Bolag'), 
        ticker=ticker, 
        yf_ticker = ticker.replace(' ', '-') + '.ST',
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


def instance_annual_report_entity(year, price_df, share_outstanding, company_obj, fundamental_obj, metric_obj = None): 
    date = datetime.datetime(int(year), 2, 15) # datum: 15 feb. year

    if metric_obj is not None: 
        return Annual_Report(
            report_date = date, 

            share_outstanding = share_outstanding,

            current_price = get_price_at_report_date(
                price_df=price_df, 
                date=date),
            
            one_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=30)),

            two_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=60)),
            
            three_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=90)),

            max_average_future_price = get_max_average_future_prices(
                price_df=price_df, 
                date=date),

            company = company_obj,
            fundamental = fundamental_obj,
            metric = metric_obj,
        )

    else: 
        return Annual_Report(
            report_date = date, 

             share_outstanding = share_outstanding,

            current_price = get_price_at_report_date(
                price_df=price_df, 
                date=date),
            
            one_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=30)),

            two_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=60)),
            
            three_month_price = get_price_at_report_date(
                price_df=price_df, 
                date=date + timedelta(days=90)),

            max_average_future_price = get_max_average_future_prices(
                price_df=price_df, 
                date=date),

            company = company_obj,
            fundamental = fundamental_obj,
        )

#
# --- Main instancing method
# 
def instance_annual_data_entities(shares_outstanding, year_df, price_df, company_obj): 
    report_columns = [col for col in year_df.columns if str(col).strip().isdigit() and len(str(col).strip()) == 4] #get all valid reports
    report_columns.sort()

    first_year = True
    shares_outstanding = float(shares_outstanding.replace(",", ".").replace(" ", "").strip()) # str to float

    for col in report_columns:
        fundamental_data = get_fundamental_data(year_df, col)
        new_fundamental = instance_fundamental_entity(fundamental_data)

        
        if not first_year: #skip metric first report
            metric_data = get_metric_data(year_df, fundamental_data, col, report_columns)
            new_metric = instance_metric_entity(metric_data=metric_data)
            new_annual_report = instance_annual_report_entity(col, price_df, shares_outstanding, company_obj,new_fundamental, new_metric)
        else: 
            new_annual_report = instance_annual_report_entity(col, price_df, shares_outstanding, company_obj, new_fundamental)

        db.session.add(new_fundamental)
        if not first_year: #skip metric report firtst
            db.session.add(new_metric)
        db.session.add(new_annual_report)

        first_year = False

def run_seeding_engine():
    export_folder = 'Borsdata - Export'

    # --- Get a list of stocks to seed in db ---
    allstocks_df = pd.read_csv(f'{export_folder}/Borsdata_AInstein_Screener.csv')
    allstocks_df = allstocks_df[["Bolagsnamn", "Antal Aktier - Senaste"]]

    # Determine the past 4 full years dynamically for Annuals
    current_year = datetime.datetime.now().year 
    target_5_years = [str(current_year - i) for i in range(1, 6)] 

    # --- Iterate through each stock and seed the database ---
    all_files = os.listdir(export_folder)
    for row in allstocks_df.itertuples():
        try: 
            # --- Load Excel sheets ---
            file_path = get_file_path_for_company(export_folder, all_files, row.Bolagsnamn)
            excel_data = get_stock_data_from_excel(file_path)

            info_df = excel_data["Info"]
            year_df = excel_data["Year"]
            quarter_df = excel_data['Quarter']
            price_df = excel_data["PriceDay"]

            # ==========================================
            # 1. ANNUAL REPORT FILTERING (Past 4 Years)
            # ==========================================
            existing_target_cols = [col for col in year_df.columns if str(col).strip() in target_5_years]
            
            oldest_required_report_date = pd.to_datetime(f"{min(target_5_years)}-02-15") 
            oldest_available_price_date = pd.to_datetime(price_df['Date']).min()

            if len(existing_target_cols) < 5 or oldest_available_price_date > oldest_required_report_date:
                print(f"    Skipping {row.Bolagsnamn}: Not enough data")
                continue

            filtered_year_df = year_df[['Report'] + sorted(existing_target_cols)].copy()

            # ==========================================
            # 2. QUARTERLY REPORT FILTERING (Past 3 Years / 12 Quarters)
            # ==========================================
            # all_quarter_cols = [col for col in quarter_df.columns if str(col).strip() != 'Report']
            # all_quarter_cols.sort() 
            # if len(all_quarter_cols) < 12:
            #     print(f"⚠️ Skipping {row.Bolagsnamn}: Only has {len(all_quarter_cols)} quarters (Needs 12 for 3 years).")
            #     continue

            # target_12_quarters = all_quarter_cols[-12:]
            # filtered_quarter_df = quarter_df[['Report'] + target_12_quarters].copy()

            # ==========================================
            # 3. DATABASE SEEDING EXECUTION
            # ==========================================
            new_company = instance_company_entity(info_df=info_df)
            
            instance_annual_data_entities( 
                shares_outstanding = row._2,
                year_df=filtered_year_df, 
                price_df=price_df, 
                company_obj=new_company) 

            # instance_quarterly_data_entities(
            #     quarter_df=filtered_quarter_df, 
            #     price_df=price_df, 
            #     company_obj=new_company)

            # --- Commit everything
            db.session.commit()
            print(f"Successfully processed database updates for {row.Bolagsnamn}")

        except Exception as e: 
            db.session.rollback() 
            print(f"  Skipping {row.Bolagsnamn}: Error: {str(e)}")


def seed_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        run_seeding_engine()

if __name__ == "__main__":
    seed_db()