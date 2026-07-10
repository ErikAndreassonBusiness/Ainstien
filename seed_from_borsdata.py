import glob
import os

import pandas as pd
import time
from datetime import date, timedelta

from app import create_app
from app.server.database import db, Company, Annual_Report, Quarterly_Report, Fundamental, Metric

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

def get_stock_data_from_excel(file_path):
    # --- Get company from Excel list ---
    return pd.read_excel(file_path, sheet_name=None)

# Get data from a report and column
def get_val(df, attr_name, col_name): 
    mask = df['Report'] == attr_name
    if mask.any():
        val = df.loc[mask, col_name].values[0]
        # Handle empty/NaN values in Excel cleanly
        if pd.notna(val): 
            return float(val)
        
        raise ValueError

def get_fundamental_data(df, col): 
    return {
        "revenue": get_val(df, 'Nettoomsättning', col),
        "ebitda": get_val(df, 'EBITDA', col),
        "ebit": get_val(df, 'Rörelseresultat', col),
        "net_income": get_val(df, 'Resultat Före Skatt', col),
        "total_assets": get_val(df, 'Summa Tillgångar', col),
        "total_equity": get_val(df, 'Summa Eget Kapital', col),
        "total_debt": get_val(df, 'Totala Skulder', col),
        "short_term_debt": get_val(df, 'Kortfristiga Skulder', col),
        "long_term_debt": get_val(df, 'Långfristiga Skulder', col),
        "current_assets": get_val(df, 'Summa Omsättningstillgångar', col),
        "cash": get_val(df, 'Kassa/Bank', col),
        "fixed_assets": get_val(df, 'Summa Anläggningstillgångar', col)
    }

def get_metric_data(df, fundamental_data, col, report_columns): 
    col_index = list(report_columns).index(col)
    prev_col = list(report_columns)[col_index - 1] if col_index > 0 else None

    prev_revenue = get_val(df, 'Nettoomsättning', prev_col) if prev_col else 0
    prev_net_income = get_val(df, 'Resultat Före Skatt', prev_col) if prev_col else 0

    # Store variables for visability
    net_debt = get_val(df, 'Nettoskuld', col)
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
def instance_company_entity(row, file_path):
    # Extract ticker from file
    filename = os.path.basename(file_path)
    ticker = filename.split('-')[0]

    new_company = Company(
        #borsdata_id=row["Börsdata ID"], #lägg till senare
        name=row.Bolagsnamn, 
        ticker=ticker)

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


def instance_annual_report_entity(companu_obj, fundamental_obj, metric_obj, df): 
    return Annual_Report(
        report_date = report_date, 
        share_outstanding = get_shares_outstanding( #fixa med shares outstanding
            bal=bal, 
            date=report_date), 

        current_price = get_price_at_report_date(
            ticker_obj=ticker_obj, 
            date=report_date),
        
        one_month_price = get_price_at_report_date(
            ticker_obj=ticker_obj, 
            date=report_date + timedelta(days=30)),

        two_month_price = get_price_at_report_date(
            ticker_obj=ticker_obj, 
            date=report_date + timedelta(days=60)),
        
        three_month_price = get_price_at_report_date(
            ticker_obj=ticker_obj, 
            date=report_date + timedelta(days=90)),

        max_average_future_price = get_max_avarage_future_prices(
            ticker_obj=ticker_obj, 
            date=report_date),

        company = company_obj,
        fundamental = fundamental_obj,
        metric = metric_obj,
    )

#
# --- Main instancing method
# 
def instance_annual_reports(year_df, company_obj): 
    report_columns = year_df.columns[2: ] #ska bli dynamisk, eller ha fixt antal år

    for col in report_columns:
        fundamental_data = get_fundamental_data(year_df, col)
        new_fundamental = instance_fundamental_entity(fundamental_data)

        metric_data = get_metric_data(year_df, fundamental_data, col, report_columns)
        new_metric = instance_metric_entity(year_df)

        new_annual_report = instance_annual_report_entity(company_obj,new_fundamental, new_metric, year_df)
        
        db.session.add(new_fundamental)
        db.session.add(new_metric)
        db.session.add(new_annual_report)

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
            file_path = get_file_path_for_company(export_folder, all_files, row.Bolagsnamn)

            # --- Load Excel sheets ---
            excel_data = get_stock_data_from_excel(file_path)
            
            new_company = instance_company_entity(row, file_path)
            
            # --- Process Annual Reports ---
            if 'Year' in excel_data:
                year_df = excel_data['Year']
                instance_annual_reports(year_df, new_company)

            # --- 3. Process Quarterly Reports (from 'Quarter' sheet) ---
            if 'Quarter' in excel_data:
                quarter_df = excel_data['Quarter']
                new_fundamental = instance_fundamental_entity(quarter_df)
                new_metric = instance_metric_entity(quarter_df)
                new_annual_report(new_company, quarter_df)
                print(quarter_df.head())

            # --- Commit everything
            db.session.commit()
            print(f"Successfully seeded {row.Bolagsnamn} ({len(year_df)} annual, {len(quarter_df)} quarterly reports)")

        except Exception as e: 
            print(f"  Skipping {row.Bolagsnamn}: Error: {str(e)}")



def seed_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        run_seeding_engine()

if __name__ == "__main__":
    seed_db()