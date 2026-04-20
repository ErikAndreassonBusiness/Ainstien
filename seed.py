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
                    "AQ.ST,", 
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

def seed_data():
    app = create_app()
    with app.app_context():
        print("Seeding Swedish Annual Fundamentals...")
        
        for symbol in TICKERS:
            print(f"Processing {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # Fetch ANNUAL data (gives 4 years)
            df = ticker.financials 
            
            if df is None or df.empty:
                print(f"No data for {symbol}")
                continue

            # Ensure Company entry exists
            company = Company.query.filter_by(ticker=symbol).first()
            if not company:
                company = Company(ticker=symbol, name=symbol)
                db.session.add(company)
                db.session.flush()

            # Iterate through the 4 years of history
            for report_date in df.columns:
                r_date = report_date.date()
                
                # Deduplication
                exists = Fundamental.query.filter_by(company_id=company.id, report_date=r_date).first()
                if not exists:
                    # Mapping Yahoo's index names to your DB columns
                    f = Fundamental(
                        company_id=company.id,
                        report_date=r_date,
                        revenue=df.loc['Total Revenue', report_date] if 'Total Revenue' in df.index else 0,
                        net_income=df.loc['Net Income', report_date] if 'Net Income' in df.index else 0,
                        eps=df.loc['Basic EPS', report_date] if 'Basic EPS' in df.index else 0
                        # You can add more attributes here as you expand
                    )
                    db.session.add(f)
            
            db.session.commit()
            print(f"Saved {symbol}")
            time.sleep(0.5) # Avoid rate limits

if __name__ == "__main__":
    seed_data()