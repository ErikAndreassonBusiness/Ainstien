# app/server/db_queries.py

from app import db
from .database import Company, Fundamental

def get_all_tickers_in_order(): 
    return Company.query.order_by(Company.ticker.asc()).all()

def get_company_by_ticker(company_ticker): 
    return Company.query.filter_by(ticker = company_ticker).first()

def sort_fundamentals_from_company(company): 
    return sorted(
        company.fundamentals, 
        key=lambda fundamental: fundamental.report_date, 
        reverse=True)
