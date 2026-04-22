"""
seed.py
Purpose: Seeds the DB with 4 years of ANNUAL fundamental data from Yahoo Finance.
Target: Swedish Mid-Cap stocks (.ST).
"""
import yfinance as yf
import time
from app import create_app
from app.database import db, Company, Fundamental

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
                    "PADEL.ST"]

def get_revenue(inc, report_date): 
    if 'Total Revenue' in inc.index: 
        return inc.loc['Total Revenue', report_date]
    else: 
        return 0
                        
def get_profit(inc, report_date):
    if 'Net Income' in inc.index: 
        return  inc.loc['Net Income', report_date]  
    else: 
        return 0

def get_ebit(inc, report_date): 
    if 'EBIT' in inc.index: 
        return inc.loc['EBIT', report_date] 
    else: 
        return 0

def get_ebitda(inc, report_date): 
    if 'EBITDA' in inc.index: 
        return inc.loc['EBITDA', report_date]
    else: 
        return 0

def calc_growth_to_percent(current_data, prev_data): 
    if prev_data < 0: 
        return (current_data - prev_data) / -prev_data
    elif prev_data == 0: 
        return 0
    else:
        return 100 * (current_data - prev_data) / prev_data

    
def calc_margin_to_percent(attribute, revenue): 
    if revenue == 0: 
        return 0
    else: 
        return 100 *attribute / revenue #convert to percent

def calc_soliditet_to_percent(bal, report_date): 
    total_assets = bal.loc['Total Assets', report_date] if 'Total Assets' in bal.index else 0
    total_equity = bal.loc['Stockholders Equity', report_date] if 'Stockholders Equity' in bal.index else 0
    return 100 * (total_equity / total_assets) if total_assets and total_assets != 0 else 0

def calc_net_debt_ebitda(bal, report_date, ebitda): 
    if ebitda == 0: 
        return 0

    if 'Total Debt' in bal.index: 
        total_debt = bal.loc['Total Debt', report_date]
    else: 
        total_debt = 0
    
    if 'Cash And Cash Equivalents' in bal.index: 
        cash = bal.loc['Cash And Cash Equivalents', report_date]
    else: 
        cash = 0
    
    return (total_debt - cash) / ebitda

def seed_data():
    app = create_app()
    with app.app_context():
        # Recreate the database
        db.drop_all()   
        db.create_all() 

        print("Seeding trading.db")
        
        for ticker in TICKERS:

            # Clean ticker (removes trailing commas if any)
            ticker = ticker.strip().replace(",", "")
            print(f"Processing {ticker}...")
            
            ticker_data = yf.Ticker(ticker)
            
            # Fetch necessary DataFrames
            inc = ticker_data.financials        # Income Statement
            bal = ticker_data.balance_sheet    # Balance Sheet
            
            if inc is None or inc.empty or bal.empty:
                print(f"Skipping {ticker}: Missing Financials or Balance Sheet")
                continue

            # If a company is not already in db, create one
            company = Company.query.filter_by(ticker=ticker).first()
            if not company:
                company = Company(ticker=ticker, name=ticker_data.info.get('shortName'))
                db.session.add(company)
                db.session.flush()

            # Sort dates from oldest to newest to ensure growth is calculated correctly
            sorted_dates = sorted(inc.columns)
            
            for i in range(1, len(sorted_dates)): #skips the first year since we need a base reveneue and profiit

                report_date = sorted_dates[i] # to get data from reports
                r_date = report_date.date() # to load the database
                    
                # 3. Manually get the previous report date
                prev_report_date = sorted_dates[i - 1]

                # Check if this specific fundemental year is already in the DB
                if Fundamental.query.filter_by(company_id=company.id, report_date=r_date).first() is None:
                    try:
                        
                        # ======= Fecth reveneue and profit =======
                        # Get previous years revenue and profit 
                        prev_rev = get_revenue(inc, prev_report_date)
                        prev_profit = get_profit(inc, prev_report_date)

                        # Get  current years revenue and profit 
                        rev_raw = get_revenue(inc, report_date)
                        net_income_raw = get_profit(inc, report_date)

                        # Fetch current years data
                        ebit_raw = get_ebit(inc, report_date)
                        ebitda_raw =  get_ebitda(inc,  report_date)

                        # ======== Calculations of x1, ... xn ========
                        rev_growth = calc_growth_to_percent(rev_raw, prev_rev)
                        profit_growth = calc_growth_to_percent(net_income_raw, prev_profit)
                        ebit_margin = calc_margin_to_percent(ebit_raw, rev_raw)
                        soliditet = calc_soliditet_to_percent(bal,report_date)
                        net_debt_ebitda = calc_net_debt_ebitda(bal, report_date, ebitda_raw)
                        
                        # ========= Add to database ==========
                        new_fundementals = Fundamental(
                            company_id=company.id,
                            report_date=r_date,
                            revenue=rev_raw / 1000000, #Convert to MSEK
                            net_income=net_income_raw / 1000000, #Convert MSEK 
                            omsattningstillvaxt=rev_growth,
                            vinsttillvaxt=profit_growth,
                            ebit_marginal=ebit_margin,
                            soliditet=soliditet,
                            net_debt_ebitda=net_debt_ebitda
                        )

                        db.session.add(new_fundementals)

                    except Exception as e:
                        print(f"Error for {ticker} on {report_date}: {e}")
            
            db.session.commit()
            print(f"Saved {ticker}")
            time.sleep(0.3)  # Slightly longer sleep for mid-caps to avoid YF blocks


if __name__ == "__main__":
    seed_data()