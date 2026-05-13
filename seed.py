"""
seed.py
Purpose: Seeds the DB with 4 years of ANNUAL fundamental data from Yahoo Finance.
Target: Swedish Mid-Cap stocks (.ST).
"""
import yfinance as yf
import pandas as pd
import time
from app import create_app
from app.server.database import db, Company, Fundamental

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
    for key in ['Total Revenue', 'Revenue', 'Operating Revenue']:
        if key in inc.index:
            revenue = inc.loc[key, report_date]
            if pd.notna(revenue) and revenue != 0:
                return revenue
    raise ValueError(f"Revenue not found for {report_date}")
                        
def get_profit(inc, report_date):
    if 'Net Income' in inc.index: 
        net_income =  inc.loc['Net Income', report_date]  

        if pd.isna(net_income): 
            raise ValueError("Net Income is NaN")
        return net_income
    else: 
        raise ValueError("Net Income not found")

def get_ebit(inc, report_date): 
    if 'EBIT' in inc.index: 
        ebit = inc.loc['EBIT', report_date] 

        if pd.isna(ebit): 
            raise ValueError("EBIT is NaN")
        return ebit
    else: 
        raise ValueError("EBIT not found")

def get_ebitda(inc, report_date): 
    if 'EBITDA' in inc.index: 
        ebitda = inc.loc['EBITDA', report_date]

        if pd.isna(ebitda): 
            raise ValueError("EBITDA is NaN")
        return ebitda
    else: 
        raise ValueError("EBITDA not found")

def calc_growth_to_percent(current_data, prev_data): 
    if prev_data < 0: 
        return (current_data - prev_data) / -prev_data
    elif prev_data == 0: 
        raise ValueError("Cannot divide with zero!")
    else:
        return 100 * (current_data - prev_data) / prev_data

    
def calc_margin_to_percent(attribute, revenue): 
    if revenue == 0: 
        raise ValueError("Cannot divide with zero!")
    else: 
        return 100 *attribute / revenue #convert to percent

def calc_soliditet_to_percent(bal, report_date): 
    if 'Total Assets' in bal.index and 'Stockholders Equity' in bal.index: 
        total_assets = bal.loc['Total Assets', report_date]
        total_equity = bal.loc['Stockholders Equity', report_date]
    else:
        raise ValueError("Total Assets or Stockholders Equity not found!")
    
    if total_assets != 0: 
        return 100 * (total_equity / total_assets) 
    else:
        raise ValueError("Cannot divide with zero!")

def calc_net_debt_ebitda(bal, report_date, ebitda): 
    if ebitda == 0: 
        raise ValueError("Cannot divide with zero!")

    if 'Total Debt' in bal.index: 
        total_debt = bal.loc['Total Debt', report_date]
    else: 
        raise ValueError("Total Debt not found")
    
    if 'Cash And Cash Equivalents' in bal.index: 
        cash = bal.loc['Cash And Cash Equivalents', report_date]
    else: 
        raise ValueError("Cash And Cash Equivalents not found")
    
    result = (total_debt - cash) / ebitda

    if pd.isna(result):
        raise ValueError("Net Debt/EBITDA is NaN")
    return result

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
            
            if inc is None or bal is None or inc.empty or bal.empty:
                print(f"Skipping {ticker}: Missing Financials or Balance Sheet")
                continue

            # Only save companies with all the data provided
            temp_fundamentals = []
            sorted_dates = sorted(inc.columns)[-4:] #get the 4 resent year
            all_years_valid = True 

            # Ensure that there is 3 years of data can be strored
            if len(sorted_dates) < 4:
                print(f"  SKIPPED: {ticker} - Not enough raw data (need 4 years, found {len(sorted_dates)})")
                continue

            for i in range(1, len(sorted_dates)): #skips the first year since we need a base reveneue and profiit

                report_date = sorted_dates[i] # to get data from reports
                r_date = report_date.date() # to load the database
                    
                # 3. Manually get the previous report date
                prev_report_date = sorted_dates[i - 1]

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
                    #net_debt_ebitda = calc_net_debt_ebitda(bal, report_date, ebitda_raw)
                    
                    # ========= Add to database ==========
                    new_year_fundementals = Fundamental(
                        report_date=r_date,
                        revenue=rev_raw / 1000000, #Convert to MSEK
                        net_income=net_income_raw / 1000000, #Convert MSEK 
                        revenue_growth_percent=rev_growth,
                        profit_growth_percent=profit_growth,
                        ebit_margin_percent=ebit_margin,
                        soliditet_percent=soliditet,
                        #net_debt_ebitda=net_debt_ebitda
                    )
                    temp_fundamentals.append(new_year_fundementals)

                # Check if any year failed
                # If so, skip the rest of the years
                except Exception as e:
                    print(f"  FAILED: Year {report_date.date()} had error: {e}")
                    all_years_valid = False
                    break  
        
            # Save only if EVERY year passed
            if all_years_valid:
                try:
                    # check so the company not already exist in db
                    # if not, create it
                    company = Company.query.filter_by(ticker=ticker).first() 
                    if not company:
                        company = Company(ticker=ticker, name=ticker_data.info.get('shortName'))
                        db.session.add(company)
                    
                    company.fundamentals = temp_fundamentals #add the fundementals to the company 
                    
                    db.session.add(company)
                    db.session.commit()
                    print(f"  SUCCESS: {ticker} saved with {len(temp_fundamentals)} years.")

                #some dataabase error
                except Exception as db_err: 
                    db.session.rollback()
                    print(f"  DATABASE ERROR for {ticker}: {db_err}")
            else:
                print(f"  SKIPPED: {ticker} due to incomplete data.")
            
            time.sleep(0.1)


if __name__ == "__main__":
    seed_data()