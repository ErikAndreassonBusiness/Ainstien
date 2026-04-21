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

def calc_revenue_growth(rev, prev_rev): 
    return (rev - prev_rev) / prev_rev if prev_rev and prev_rev != 0 else 0

def calc_profit_growth(net_income, prev_vinst): 
    return (net_income - prev_vinst) / abs(prev_vinst) if prev_vinst and prev_vinst != 0 else 0

def calc_ebit_margin(ebit, rev): 
    return (ebit / rev) if rev and rev != 0 else 0

def calc_soliditet(bal, report_date): 
    total_assets = bal.loc['Total Assets', report_date] if 'Total Assets' in bal.index else 0
    total_equity = bal.loc['Stockholders Equity', report_date] if 'Stockholders Equity' in bal.index else 0
    return (total_equity / total_assets) if total_assets and total_assets != 0 else 0

def calc_net_debt_ebitda(bal, report_date, ebitda): 
    total_debt = bal.loc['Total Debt', report_date] if 'Total Debt' in bal.index else 0
    cash = bal.loc['Cash And Cash Equivalents', report_date] if 'Cash And Cash Equivalents' in bal.index else 0
    net_debt = total_debt - cash
    return (net_debt / ebitda) if ebitda and ebitda != 0 else 0

def add_fundementals_to_db(id, r_date, rev, net_income, rev_growth, vinst_growth, ebit_margin, soliditet, net_debt_ebitda): 
    fundementals = Fundamental(
        company_id=id,
        report_date=r_date,
        revenue=rev,
        net_income=net_income,
        omsattningstillvaxt=rev_growth,
        vinsttillvaxt=vinst_growth,
        ebit_marginal=ebit_margin,
        soliditet=soliditet,
        net_debt_ebitda=net_debt_ebitda
    )

    db.session.add(fundementals)

def seed_data():
    app = create_app()
    with app.app_context():
        print("Wiping and rebuilding database...")
        db.drop_all()   
        db.create_all() 

        print("Seeding Swedish Annual Fundamentals with Ratios...")
        
        for symbol in TICKERS:
            # Clean ticker (removes trailing commas if any)
            symbol = symbol.strip().replace(",", "")
            print(f"Processing {symbol}...")
            
            ticker = yf.Ticker(symbol)
            
            # Fetch necessary DataFrames
            inc = ticker.financials        # Income Statement
            bal = ticker.balance_sheet    # Balance Sheet
            cf = ticker.cashflow          # Cash Flow (optional, for EBITDA)
            
            if inc is None or inc.empty or bal.empty:
                print(f"Skipping {symbol}: Missing Financials or Balance Sheet")
                continue

            # Ensure Company entry exists
            company = Company.query.filter_by(ticker=symbol).first()
            if not company:
                company = Company(ticker=symbol, name=symbol)
                db.session.add(company)
                db.session.flush()

            # ... (Inside the ticker loop, after fetching inc, bal, cf) ...

            # Sort dates from oldest to newest to ensure growth is calculated correctly
            # i.e., [2020, 2021, 2022, 2023]
            sorted_dates = sorted(inc.columns)
            
            for i in range(len(sorted_dates)):
                report_date = sorted_dates[i]
                r_date = report_date.date()
                
                # 2. Don't sotre data for the first year
                if i == 0:
                    continue
                    
                # 3. Manually get the previous report date
                prev_date = sorted_dates[i - 1]

                # Check if this specific year is already in the DB
                if Fundamental.query.filter_by(company_id=company.id, report_date=r_date).first():
                    continue

                try:
                    # Current Year Data
                    rev = inc.loc['Total Revenue', report_date] if 'Total Revenue' in inc.index else 0
                    ebit = inc.loc['EBIT', report_date] if 'EBIT' in inc.index else 0
                    ebitda = inc.loc['EBITDA', report_date] if 'EBITDA' in inc.index else None
                    net_income = inc.loc['Net Income', report_date] if 'Net Income' in inc.index else 0
                    
                    # Previous Year Data (for growth)
                    prev_rev = inc.loc['Total Revenue', prev_date] if 'Total Revenue' in inc.index else 0
                    prev_vinst = inc.loc['Net Income', prev_date] if 'Net Income' in inc.index else 0

                    # Calculations
                    rev_growth = (rev - prev_rev) / prev_rev if prev_rev and prev_rev != 0 else 0
                    vinst_growth = calc_profit_growth(net_income, prev_vinst)
                    ebit_margin = calc_ebit_margin(ebit, rev)
                    soliditet = calc_soliditet(bal,report_date)
                    net_debt_ebitda = calc_net_debt_ebitda(bal)

                    #Add to database
                    add_fundementals_to_db(company.id, r_date, rev, net_income, 
                                                                rev_growth, vinst_growth, ebit_margin, 
                                                                soliditet, net_debt_ebitda)

                except Exception as e:
                    print(f"Error for {symbol} on {report_date}: {e}")
            
            db.session.commit()
            print(f"Saved {symbol}")
            time.sleep(0.3)  # Slightly longer sleep for mid-caps to avoid YF blocks


if __name__ == "__main__":
    seed_data()