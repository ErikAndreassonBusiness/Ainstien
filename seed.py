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

goodTICKERS = [
    "NMAN.ST",      # Nederman Holding
    "VBG-B.ST",     # VBG Group
    "BERG-B.ST",     # Bergman & Beving
    "XANO-B.ST",    # XANO Industri
    "CTTS.ST",      # CTT Systems
    "INSTAL.ST",    # Instalco
    "SDIP-B.ST",      # Sdiptech
    "EPEN.ST",     # Ependion
    "REJL-B.ST",    # Rejlers
    "HANZA.ST",     # Hanza
    "INWI.ST",      # Inwido
    "FG.ST",        # Fasadgruppen
    "GREEN.ST",    # Green Landscaping Group
    "VOLO.ST",      # Volati
    "COOR.ST",      # Coor Service Management
    "ALLIGO-B.ST"   # Alligo
]

TICKERS = ["8TRA.ST", 
                    "VOLO.ST", 
                    "PEAB-B.ST", 
                    "HUSQ-B.ST", 
                    "BUFAB.ST", 
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
                    "KARNEL.ST", #-B?
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
                    "STWK.ST", 
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
                    "NOTE.ST", 
                    "NMAN.ST",      # Nederman Holding
                    "VBG-B.ST",     # VBG Group
                    "BERG-B.ST",     # Bergman & Beving
                    "XANO-B.ST",    # XANO Industri
                    "CTTS.ST",      # CTT Systems
                    "INSTAL.ST",    # Instalco
                    "SDIP-B.ST",      # Sdiptech
                    "EPEN.ST",     # Ependion
                    "REJL-B.ST",    # Rejlers
                    "HANZA.ST",     # Hanza
                    "INWI.ST",      # Inwido
                    "FG.ST",        # Fasadgruppen
                    "GREEN.ST",    # Green Landscaping Group
                    "VOLO.ST",      # Volati
                    "COOR.ST",      # Coor Service Management
                    "ALLIGO-B.ST"]   # Alligo

def clean_ticker_list(): 
    """Convert all tickers to the correct format"""
    cleaned_list = []
    
    for ticker in TICKERS: 
        if ticker not in cleaned_list:
            ticker = ticker.strip().replace(",", "")
            cleaned_list.append(ticker)

    return cleaned_list

def check_if_inc_bal_exists(inc, bal): 
    if inc is None or bal is None or inc.empty or bal.empty:
        raise ValueError("Abort!")

def check_if_four_reports_exists(report_dates):
    if len(report_dates) < 4:
        raise ValueError("Abort!")

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
        #substansvarde = get_substansvarde(bal, date),
        revenue=get_revenue(inc, date),
        depreciation=get_depreciation(inc, date),
        EBITDA=get_ebitda(inc, date),
        EBIT=get_ebit(inc, date),
        net_income=get_net_income(inc, date),
        total_assets=get_total_assets(bal, date),
        total_equity=get_total_equity(bal, date),
        total_debt=get_total_debt(bal, date),
        short_term_debt=get_short_debt(bal, date),
        long_term_debt=get_long_debt(bal, date),
        current_assets=get_current_assets(bal, date),
        inventory=get_inventory(bal, date),
        account_receiveables=get_receivables(bal, date),
        cash=get_cash(bal, date),
        fixed_assets=get_fixed_assets(bal, date),
        goodwill=get_goodwill(bal, date)
    )

def instance_metric_entity(report_obj, date, prev_date, inc, bal): 
    return Metric(
        report=report_obj,
        revenue_growth_percent=get_revenue_growth(inc, date, prev_date),
        profit_growth_percent=get_profit_growth(inc, date, prev_date),
        quick_ratio_percent=get_quick_ratio(bal, date),
        net_debt_ebitda_ratio=get_net_debt_ebitda(inc, bal, date),
        equity_ratio_percent=get_equity_ratio(bal, date),
        assets_turnover_ratio=get_asset_turnover(inc, bal, date),
        inventory_turnover_ratio=get_inventory_turnover(inc, bal, date),
        ROA=get_roa(inc, bal, date),
        ROE=get_roe(inc, bal, date),
        ROI=get_roi(inc, bal, date),
        #gross_profit_margin_percent=get_gross_margin(inc, date),
        ebit_margin_percent=get_ebit_margin(inc, date),
        profit_margin_percent=get_profit_margin(inc, date)
    )

def instance_entities(ticker_obj, new_company, date, prev_date, inc, bal): 
    new_report = instance_report_entity(ticker_obj, date, new_company, inc, bal)
    new_fundamental = instance_fundamental_entity(new_report, date, inc, bal)

    if prev_date != date:
        new_metric = instance_metric_entity(new_report, date, prev_date, inc, bal)

    db.session.add(new_report)
    db.session.add(new_fundamental)

    if prev_date != date:
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

            prev_date = report_dates[0]
            for date in report_dates: 
                instance_entities(
                    ticker_obj = ticker_obj,
                    new_company=new_company, 
                    date=date, 
                    prev_date = prev_date,
                    inc=inc, 
                    bal=bal
                )

                prev_date = date

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