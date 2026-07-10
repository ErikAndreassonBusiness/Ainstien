# app/server/db_queries.py

from app import db
import pandas as pd
from .database import Company, Fundamental, Metric, Annual_Report, Quarterly_Report
from sqlalchemy.orm import joinedload

# ============== Companies ================
def get_company_fundamentals_history(ticker):
    """
    Fetches a specific company and all its historical annual reports with fundamental data.
    """
    company = Company.query.options(
        joinedload(Company.annual_reports).joinedload(Annual_Report.fundamental)
    ).filter_by(ticker=ticker).first()
    
    if not company:
        return None
    
    # Sort annual reports from oldest to newest 
    sorted_reports = sorted(company.annual_reports, key=lambda r: r.report_date)

    return {
        "company_id": company.id,
        "name": company.name,
        "ticker": company.ticker,
        "history": [report.to_dict() for report in sorted_reports]
    }

def get_dashboard_market_data():
    """
    Fetches all companies, their latest annual reports, and associated fundamental data.
    """
    companies = Company.query.options(
        joinedload(Company.annual_reports).joinedload(Annual_Report.fundamental),
    ).all()
    
    dashboard_list = []

    for company in companies:
        revenue = 0.0
        ebit = 0.0

        if company.annual_reports:
            latest_report = max(company.annual_reports, key=lambda r: r.report_date)
            
            fundamental = latest_report.fundamental
            if fundamental:
                revenue = fundamental.revenue
                ebit = fundamental.ebit

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


# ============ For Models ===============
def build_dataframe_for_models(metric_features_enabled):
    """
    Builds a clean training DataFrame by safely extracting database column values 
    instead of using raw Python dir() which includes database metadata.
    """
    data_rows = []
    
    fundamental_cols = Fundamental.get_attribute_names()
    metric_cols = Metric.get_attribute_names()

    for company in get_all_companies():
        reports = get_all_annual_reports(company)
        reports_to_process = reports[1:] if metric_features_enabled else reports

        for report in reports_to_process:
            row = {
                "max_average_future_price": report.max_average_future_price,
                "one_month_price": report.one_month_price, 
                "two_month_price": report.two_month_price,
                "three_month_price": report.three_month_price,
                "share_outstanding": report.share_outstanding,
                "current_price": report.current_price,
            }
        
            # Safely extract pure data values
            fund_obj = get_all_fundamentals(report)
            if fund_obj:
                for attr in fundamental_cols:
                    row[f"fundamental_{attr}"] = getattr(fund_obj, attr, None)
                    
            metric_obj = get_all_metrics(report)
            if metric_obj:
                for attr in metric_cols:
                    row[f"metric_{attr}"] = getattr(metric_obj, attr, None)
        
            data_rows.append(row)
            
    return pd.DataFrame(data_rows)


# ============== Getters ================
def get_all_companies(): 
    return Company.query.all()

def get_all_annual_reports(company):
    return company.annual_reports

def get_all_quarterly_reports(company):
    return company.quarterly_reports

def get_all_fundamentals(report):
    return report.fundamental

def get_all_metrics(report):
    return report.metric

def get_fundamentals_attrbiute_names():
    return Fundamental.get_attribute_names()

def get_metrics_attrbiute_names():
    return Metric.get_attribute_names()