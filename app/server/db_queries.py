# app/server/db_queries.py

from app import db
from .database import Company, Fundamental, Report
from sqlalchemy.orm import joinedload

# ============== Companies ================
def get_company_fundamentals_history(ticker):
    """
    Fetches a specific company and all its historical reports with fundamental data.
    Returns a clean dictionary tailored for frontend consumption.
    """

    company = Company.query.options(
        joinedload(Company.reports).joinedload(Report.fundamental)
    ).filter_by(ticker=ticker).first()
    
    # Sort reports from oldest to newest 
    sorted_reports = sorted(company.reports, key=lambda r: r.report_date)

    return {
        "company_id": company.id,
        "name": company.name,
        "ticker": company.ticker,
        "history": [report.to_dict() for report in sorted_reports]
    }

def get_dashboard_market_data():
    """
    Fetches all companies, their latest reports, and associated fundamental/metric data.
    Uses nested joinedload to efficiently fetch related data in a single query.
    """
    # 1. Fetch all companies and eager-load nested reports, fundamentals, and metrics
    companies = Company.query.options(
        joinedload(Company.reports).joinedload(Report.fundamental),
    ).all()
    
    dashboard_list = []

    for company in companies:
        # Default values if no report or metrics exist
        revenue = 0.0
        ebit = 0.0

        # 2. Get the latest report based on report_date
        if company.reports:
            latest_report = max(company.reports, key=lambda r: r.report_date)
            
            # Access the connected metric row safely
            fundamental = latest_report.fundamental
            if fundamental:
                revenue = fundamental.revenue
                ebit = fundamental.EBIT

        # 3. Build the lightweight dictionary for the dashboard
        company_data = {
            "name": company.name,
            "ticker": company.ticker,
            "revenue": revenue,
            "ebit": ebit,
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



