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

#
# --- Instances of Entities ---
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


def instance_fundamental_entity(df):
    pass
    # return Fundamental(
    #     report_date=date,
    #     revenue=inc.get('Revenue', 0.0),
    #     ebit=inc.get('EBIT', 0.0),
    #     net_income=inc.get('Net Income', 0.0),
    #     total_assets=bal.get('Total Assets', 0.0),
    #     total_liabilities=bal.get('Total Liabilities', 0.0),
    #     equity=bal.get('Equity', 0.0)
    # )

def instance_metric_entity(df):
    pass
    # return Metric(
    #     report_date=date,
    #     current_ratio=bal.get('Current Ratio', 0.0),
    #     debt_to_equity=bal.get('Debt to Equity', 0.0),
    #     return_on_assets=inc.get('Return on Assets', 0.0),
    #     return_on_equity=inc.get('Return on Equity', 0.0)
    # )

def instance_report_entity(companu_obj, df): 
    return Annual_Report(
        report_date = report_date, 
        share_outstanding = get_shares_outstanding(
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
                new_fundamental = instance_fundamental_entity(year_df)
                new_metric = instance_metric_entity(year_df)
                new_annual_report(new_company, year_df)

                print(year_df.head())

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