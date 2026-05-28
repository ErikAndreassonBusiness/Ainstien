"""
seed.py
Purpose: Seeds the DB with 4 years of ANNUAL fundamental data from Yahoo Finance.
Target: Swedish Mid-Cap stocks (.ST).
"""

import pandas as pd
import time

from app import create_app
from app.server.database import db, Company, Report, Fundamental, Metric

from seed_db.seed_reports import *
from seed_db.seed_metrics import *
from seed_db.seed_fundementals import *

# Start with a small list to test, then add your full 200
TICKERS = ["8TRA.ST", 
                    "VOLO.ST", 
                    "PEAB-B.ST", 
                    "HUSQ-B.ST", 
                    "BUFAB.SR", 
                    "NCC-B.ST", 
                    "BRAV.ST", 
                    "AQ.ST", 
                    "OEM-B.ST", 
                    "STOR-B.ST", 
                    "BEIA-B.ST", 
                    "SYSR.ST", 
                    "EPRO-B.ST", 
                    "AFRY.ST", 
                    "LIAB.ST", 
                    "ALIG.ST", 
                    "RATO-B.ST", 
                    "PLEJD.ST", 
                    "VSURE.ST", 
                    "ENGCON-B.ST", 
                    "INSTAL.ST", 
                    "INWI.ST", 
                    "SPID-B.ST", 
                    "MILDEF.ST", 
                    "BERG-B.ST", 
                    "KAR.ST", 
                    "ALLIGO-B.ST", 
                    "MMGR-B.ST", 
                    "GOTL-B.ST", 
                    "TROAX.ST", 
                    "COOR.ST", 
                    "FAG.ST", 
                    "NYAB.ST", 
                    "ITAB.ST", 
                    "FMM-B.ST", 
                    "KARNEL-B.ST", 
                    "REJL-B.ST", 
                    "VESTUM.ST", 
                    "XANO-B.ST", 
                    "GOMX.ST", 
                    "SVED-B.ST", 
                    "BTS-B.ST", 
                    "TEQ.ST", 
                    "SVIK.ST", 
                    "GREEN.ST", 
                    "ARSO.ST", 
                    "BYGGP.ST", 
                    "FG.ST", 
                    "BERNER-B.ST", 
                    "VSSAB-B.ST", 
                    "CTT.ST", 
                    "ELAN-B.ST",
                    "CCC.ST", 
                    "PCELL.ST", 
                    "INISS-B.ST", 
                    "EWRK.ST", 
                    "FIRE.ST", 
                    "VPAB-B.ST", 
                    "CTEK.ST", 
                    "ACC.ST", 
                    "SALT-B.ST", 
                    "W5.ST", 
                    "PROF-B.ST", 
                    "RAIL.ST", 
                    "HAKI-B.ST", 
                    "NORB-B.ST", 
                    "SINT.ST", 
                    "FNM.ST", 
                    "GARO.ST", 
                    "CNCJO-B.ST", 
                    "CARE.ST", 
                    "PRIC-B.ST", 
                    "INFREA.ST", 
                    "SUMMAS.ST", 
                    "AVT-B.ST", 
                    "TERNOR.ST", 
                    "FLEXQ.ST", 
                    "WTW-A.ST", 
                    "DEDI.ST", 
                    "QAIR.ST", 
                    "SBOK.ST", 
                    "META.ST", 
                    "AGES-B.ST", 
                    "OCUN-B.ST", 
                    "SUSG.ST", 
                    "FERRO.ST", 
                    "FREEM.ST", 
                    "CALVIK.ST", 
                    "IMPC.ST", 
                    "TURA.ST", 
                    "PION-B.ST",
                    "WBGR-B.ST", 
                    "NETEL.ST", 
                    "STW.ST", 
                    "SES.ST", 
                    "ENVI-B.ST", 
                    "LYGRD.ST", 
                    "HULT-B.ST", 
                    "DRIL.ST", 
                    "OXE.ST", 
                    "NOTEK.ST", 
                    "OPTI.ST", 
                    "NEPA.ST", 
                    "WISE.ST", 
                    "STWK.ST", 
                    "BIOEX.ST", 
                    "LEVEL.ST", 
                    "TSEC.ST", 
                    "VIMAB.ST", 
                    "ESGR-B.ST", 
                    "AXOLOT.ST", 
                    "SAXG.ST", 
                    "GGEO.ST", 
                    "RAMSH.ST", 
                    "BAWAT.ST", 
                    "CI.ST", 
                    "HEXI.ST", 
                    "AERW-B.ST", 
                    "MBBAB.ST", 
                    "HELIO.ST", 
                    "NFGAB.ST", 
                    "BOMILL.ST", 
                    "BRILL.ST", 
                    "ABAS.ST", 
                    "IRIS.ST", 
                    "CIRCHE.ST", 
                    "EASY-B.ST", 
                    "HEGR.ST", 
                    "MANTEX.ST", 
                    "PCOM-B.ST", 
                    "ZENZIP-B.ST", 
                    "PADEL.ST", 
                    "NOTE.ST"]

def clean_ticker_list(): 
    """Convert all tickers to the correct format"""
    cleaned_list = []
    for ticker in TICKERS: 
        ticker = ticker.strip().replace(",", "")
        cleaned_list.append(ticker)

    return cleaned_list

def check_if_inc_bal_exists(inc, bal): 
    if inc is None or bal is None or inc.empty or bal.empty:
        raise ValueError("Abort!")

def check_if_four_reports_exists(report_dates):
    if len(report_dates) < 4:
        raise ValueError("Abort!")

# def instance_report_entity(report_date, company_obj, inc, bal): 
#     return Report(
#                     report_date = date, 
#                     share_outstanding = get_shares_outstanding(), 
#                     current_price = get_price_at_report_date(),
#                     max_average_future_price = get_max_avarage_future_prices(),
#                     company = new_company,
#                 )

# def instance_fundamental_entity(report_obj, date, inc, bal): 
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

# def instance_metric_entity(report_obj, date, inc, bal): 
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

def instance_company_entity(ticker, ticker_obj): 
    return Company(
        ticker=ticker, 
        name=ticker_obj.info.get('shortName', "Unknown Company")
    )

def instance_report_entity(ticker_obj, report_date, company_obj, inc, bal): 
    return Report(
        report_date = report_date, 
        share_outstanding = get_shares_outstanding(
            bal=bal, 
            date=report_date), 

        current_price = get_price_at_report_date(
            ticker_obj=ticker_obj, 
            date=report_date),

        max_average_future_price = get_max_avarage_future_prices(
            ticker_obj=ticker_obj, 
            date=report_date),

        company = company_obj,
    )

def instance_fundamental_entity(report_obj, date, inc, bal): 
    return Fundamental(
        report=report_obj, 
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

def instance_metric_entity(report_obj, date, inc, bal): 
    return Metric(
        report=report_obj,
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

def instance_entities(ticker_obj, new_company, date, inc, bal): 
    new_report = instance_report_entity(ticker_obj, date, new_company, inc, bal)
    new_fundamental = instance_fundamental_entity(new_report, date, inc, bal)
    new_metric = instance_metric_entity(new_report, date, inc, bal)

    db.session.add(new_report)
    db.session.add(new_fundamental)
    db.session.add(new_metric)

# === Main Logic Function ===
def run_seeding_engine(): 
    for ticker in clean_ticker_list():
        try:
            print(f"Processing {ticker}...")
            ticker_obj = yf.Ticker(ticker)

            inc = ticker_obj.income_stmt
            bal = ticker_obj.balance_sheet

            report_dates = sorted(inc.columns)[-4:] #For recent years, not report date!!!!

            check_if_inc_bal_exists(inc, bal) #raise Value if not
            check_if_four_reports_exists(report_dates) #raise Value if not

            new_company = instance_company_entity(ticker, ticker_obj)

            for date in report_dates: 
                instance_entities(
                    ticker_obj = ticker_obj,
                    new_company=new_company, 
                    date=date, 
                    inc=inc, 
                    bal=bal
                )

            db.session.add(new_company)
            db.session.commit()
            print(f"  Successfully seeded {ticker}")

        except ValueError as e: 
            print(f"  Skipping {ticker}: Missing Financials or Balance Sheet")


# === Main Seeding Function ===
def seed_data(): 
    app = create_app()
    with app.app_context():
        db.drop_all()   
        db.create_all()
        
        run_seeding_engine()

if __name__ == "__main__":
    seed_data()