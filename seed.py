"""
seed.py
Purpose: Seeds the DB with 4 years of ANNUAL fundamental data from Yahoo Finance.
Target: Swedish Mid-Cap stocks (.ST).
"""
import yfinance as yf
import pandas as pd
from datetime import timedelta
import time

from app import create_app
from app.server.database import db, Company, Report, Fundamental, Metric
from seed_db.seed_metrics import *
from seed_db.seed_fundementals import *

# Start with a small list to test, then add your full 200
TICKERS = ["8TRA.ST", 
                    "VOLO.ST", 
                    "PEAB-B.ST"]
                    # "HUSQ-B.ST", 
                    # "BUFAB.SR", 
                    # "NCC-B.ST", 
                    # "BRAV.ST", 
                    # "AQ.ST", 
                    # "OEM-B.ST", 
                    # "STOR-B.ST", 
                    # "BEIA-B.ST", 
                    # "SYSR.ST", 
                    # "EPRO-B.ST", 
                    # "AFRY.ST", 
                    # "LIAB.ST", 
                    # "ALIG.ST", 
                    # "RATO-B.ST", 
                    # "PLEJD.ST", 
                    # "VSURE.ST", 
                    # "ENGCON-B.ST", 
                    # "INSTAL.ST", 
                    # "INWI.ST", 
                    # "SPID-B.ST", 
                    # "MILDEF.ST", 
                    # "BERG-B.ST", 
                    # "KAR.ST", 
                    # "ALLIGO-B.ST", 
                    # "MMGR-B.ST", 
                    # "GOTL-B.ST", 
                    # "TROAX.ST", 
                    # "COOR.ST", 
                    # "FAG.ST", 
                    # "NYAB.ST", 
                    # "ITAB.ST", 
                    # "FMM-B.ST", 
                    # "KARNEL-B.ST", 
                    # "REJL-B.ST", 
                    # "VESTUM.ST", 
                    # "XANO-B.ST", 
                    # "GOMX.ST", 
                    # "SVED-B.ST", 
                    # "BTS-B.ST", 
                    # "TEQ.ST", 
                    # "SVIK.ST", 
                    # "GREEN.ST", 
                    # "ARSO.ST", 
                    # "BYGGP.ST", 
                    # "FG.ST", 
                    # "BERNER-B.ST", 
                    # "VSSAB-B.ST", 
                    # "CTT.ST", 
                    # "ELAN-B.ST",
                    # "CCC.ST", 
                    # "PCELL.ST", 
                    # "INISS-B.ST", 
                    # "EWRK.ST", 
                    # "FIRE.ST", 
                    # "VPAB-B.ST", 
                    # "CTEK.ST", 
                    # "ACC.ST", 
                    # "SALT-B.ST", 
                    # "W5.ST", 
                    # "PROF-B.ST", 
                    # "RAIL.ST", 
                    # "HAKI-B.ST", 
                    # "NORB-B.ST", 
                    # "SINT.ST", 
                    # "FNM.ST", 
                    # "GARO.ST", 
                    # "CNCJO-B.ST", 
                    # "CARE.ST", 
                    # "PRIC-B.ST", 
                    # "INFREA.ST", 
                    # "SUMMAS.ST", 
                    # "AVT-B.ST", 
                    # "TERNOR.ST", 
                    # "FLEXQ.ST", 
                    # "WTW-A.ST", 
                    # "DEDI.ST", 
                    # "QAIR.ST", 
                    # "SBOK.ST", 
                    # "META.ST", 
                    # "AGES-B.ST", 
                    # "OCUN-B.ST", 
                    # "SUSG.ST", 
                    # "FERRO.ST", 
                    # "FREEM.ST", 
                    # "CALVIK.ST", 
                    # "IMPC.ST", 
                    # "TURA.ST", 
                    # "PION-B.ST",
                    # "WBGR-B.ST", 
                    # "NETEL.ST", 
                    # "STW.ST", 
                    # "SES.ST", 
                    # "ENVI-B.ST", 
                    # "LYGRD.ST", 
                    # "HULT-B.ST", 
                    # "DRIL.ST", 
                    # "OXE.ST", 
                    # "NOTEK.ST", 
                    # "OPTI.ST", 
                    # "NEPA.ST", 
                    # "WISE.ST", 
                    # "STWK.ST", 
                    # "BIOEX.ST", 
                    # "LEVEL.ST", 
                    # "TSEC.ST", 
                    # "VIMAB.ST", 
                    # "ESGR-B.ST", 
                    # "AXOLOT.ST", 
                    # "SAXG.ST", 
                    # "GGEO.ST", 
                    # "RAMSH.ST", 
                    # "BAWAT.ST", 
                    # "CI.ST", 
                    # "HEXI.ST", 
                    # "AERW-B.ST", 
                    # "MBBAB.ST", 
                    # "HELIO.ST", 
                    # "NFGAB.ST", 
                    # "BOMILL.ST", 
                    # "BRILL.ST", 
                    # "ABAS.ST", 
                    # "IRIS.ST", 
                    # "CIRCHE.ST", 
                    # "EASY-B.ST", 
                    # "HEGR.ST", 
                    # "MANTEX.ST", 
                    # "PCOM-B.ST", 
                    # "ZENZIP-B.ST", 
                    # "PADEL.ST"]


def clean_ticker_list(): 
    """Convert all tickers to the correct format"""
    cleaned_list = []
    for ticker in TICKERS: 
        ticker = ticker.strip().replace(",", "")
        cleaned_list.append(ticker)

    return cleaned_list

def inc_and_bal_exists(ticker, inc, bal): 
    if inc is None or bal is None or inc.empty or bal.empty:
        print(f"  Skipping {ticker}: Missing Financials or Balance Sheet")
        return False

    return True

def four_reports_exists(ticker, report_dates):
    if len(report_dates) < 4:
        return False
    
    return True

# def instance_company_entity(): 
#     return Company(
#                 ticker = ticker, 
#                 name = ticker_data.info.get('shortName')
#             )

# def instance_report_entitiy(): 
#     return Report(
#                     report_date = date, 
#                     share_outstanding = get_shares_outstanding(), 
#                     current_price = get_price_at_report_date(),
#                     max_average_future_price = get_max_avarage_future_prices(),
#                     company = new_company,
#                 )

# def instance_fundemental_entity(): 
#     return Fundamental(
#                     report=new_report,
#                     revenue=get_revenue(inc, r_date),
#                     depreciation=get_depreciation(inc, r_date),
#                     EBITDA=get_ebitda(inc, r_date),
#                     EBIT=get_ebit(inc, r_date),
#                     net_income=get_net_income(inc, r_date),
#                     total_assets=get_total_assets(bal, r_date),
#                     total_equity=get_total_equity(bal, r_date),
#                     total_debt=get_total_debt(bal, r_date),
#                     short_term_debt=get_short_debt(bal, r_date),
#                     long_term_debt=get_long_debt(bal, r_date),
#                     current_assets=get_current_assets(bal, r_date),
#                     inventory=get_inventory(bal, r_date),
#                     account_receiveables=get_receivables(bal, r_date),
#                     cash=get_cash(bal, r_date),
#                     fixed_assets=get_fixed_assets(bal, r_date),
#                     goodwill=get_goodwill(bal, r_date)
#                 )

# def instance_metric_entity(): 
#     return Metric(
#                     report=new_report,
#                     revenue_growth_percent=get_rev_growth(inc, r_date),
#                     profit_growth_percent=get_profit_growth(inc, r_date),
#                     quick_ratio_percent=get_quick_ratio(bal, r_date),
#                     net_debt_ebitda_ratio=get_net_debt_ebitda(inc, bal, r_date),
#                     equity_ratio_percent=get_equity_ratio(bal, r_date),
#                     assets_turnover_ratio=get_asset_turnover(inc, bal, r_date),
#                     inventory_turnover_ratio=get_inv_turnover(inc, bal, r_date),
#                     ROA=get_roa(inc, bal, r_date),
#                     ROE=get_roe(inc, bal, r_date),
#                     ROI=get_roi(inc, bal, r_date),
#                     gross_profit_margin_percent=get_gross_margin(inc, r_date),
#                     ebit_margin_percent=get_ebit_margin(inc, r_date),
#                     profit_margin_percent=get_profit_margin(inc, r_date)
#                 )

def instance_company_entity(ticker, ticker_data): 
    return Company(
        ticker=ticker, 
        # Using .get() with a default in case info is empty
        name=ticker_data.info.get('shortName', "Unknown Company")
    )

def instance_report_entity(report_date, company_obj): 
    return Report(
        report_date=report_date, 
        share_outstanding=0, 
        current_price=0.0,
        max_average_future_price=0.0,
        company=company_obj  # Links to the Company object
    )

def instance_fundamental_entity(report_obj): 
    return Fundamental(
        report=report_obj, # Links to the Report object
        substansvarde=0.0,
        revenue=0.0,
        depreciation=0.0,
        EBITDA=0.0,
        EBIT=0.0,
        net_income=0.0,
        total_assets=0.0,
        total_equity=0.0,
        total_debt=0.0,
        short_term_debt=0.0,
        long_term_debt=0.0,
        current_assets=0.0,
        inventory=0.0,
        account_receiveables=0.0,
        cash=0.0,
        fixed_assets=0.0,
        goodwill=0.0
    )

def instance_metric_entity(report_obj): 
    return Metric(
        report=report_obj, # Links to the Report object
        revenue_growth_percent=0.0,
        profit_growth_percent=0.0,
        quick_ratio_percent=0.0,
        net_debt_ebitda_ratio=0.0,
        equity_ratio_percent=0.0,
        assets_turnover_ratio=0.0,
        inventory_turnover_ratio=0.0,
        ROA=0.0,
        ROE=0.0,
        ROI=0.0,
        gross_profit_margin_percent=0.0,
        ebit_margin_percent=0.0,
        profit_margin_percent=0.0
    )

# === Main Seed Function ===
def seed_data(): 
    app = create_app()
    with app.app_context():
        db.drop_all()   
        db.create_all()

        for ticker in clean_ticker_list():
            print(f"Processing {ticker}...")
            ticker_data = yf.Ticker(ticker)

            inc = ticker_data.income_stmt
            bal = ticker_data.balance_sheet

            report_dates = sorted(inc.columns)[-4:] #For recent years, not report date!!!!

            if inc_and_bal_exists(ticker, inc, bal) and four_reports_exists(ticker, report_dates): 
                new_company = instance_company_entity(ticker, ticker_data)

                for date in report_dates: 
                    new_report = instance_report_entity(date, new_company)

                    new_fundamental = instance_fundamental_entity(new_report)
                    new_metric = instance_metric_entity(new_report)
            
            db.session.add(new_report)
            db.session.add(new_fundamental)
            db.session.add(new_metric)

        db.session.commit()


if __name__ == "__main__":
    seed_data()