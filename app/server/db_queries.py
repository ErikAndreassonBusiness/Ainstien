# app/server/db_queries.py

from app import db
from .database import Company, Fundamental
from sqlalchemy.orm import joinedload

# ============== Companies ================
def get_company_by_ticker(ticker): 
    company = Comapny.query.filter_by(ticker).first()
    return company.serialize_and_its_fundamentals()

def get_dashboard_market_data():
    """
    Fetches all companies and their most recent fundamental report data.
    Uses joinedload to prevent the N+1 query performance problem.
    """
    # 1. Fetch all companies and their fundamentals
    companies = Company.query.options(joinedload(Company.fundamentals)).all()
    
    dashboard_list = []

    #Get latest report
    for company in companies:
        latest_report = None
        if company.fundamentals:
            latest_report = max(company.fundamentals, key=lambda fundamental: fundamental.report_date)

        # 3. Build a lightweight dictionary for the Dashboard table
        # If no report exists, we default to 0 to prevent the frontend from breaking
        company_data = {
            "name": company.name,
            "ticker": company.ticker,
            "revenue_growth": latest_report.revenue_growth_percent,
            "ebit_margin": latest_report.ebit_margin_percent,
            "soliditet": latest_report.soliditet_percent,
        }
        
        dashboard_list.append(company_data)

    return dashboard_list

def get_all_tickers_in_order(): 
    return Company.query.order_by(Company.ticker.asc()).all()

def get_company_by_ticker(company_ticker): 
    return Company.query.filter_by(ticker = company_ticker).first()

def sort_fundamentals_from_company(company): 
    return sorted(
        company.fundamentals, 
        key=lambda fundamental: fundamental.report_date, 
        reverse=True)

