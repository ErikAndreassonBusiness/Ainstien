# app/server/routes.py
from flask import render_template, current_app as app
from .db_queries import (
    get_all_tickers_in_order, 
    get_company_by_ticker, 
    sort_fundamentals_from_company
)
from .live_market import get_live_market_data
# ===== Home (Dashboard) page =======
@app.route('/')
def dashboard():
    return render_template('dashboard.html', companies=get_all_tickers_in_order())

# ====== Company Info page ========
@app.route('/company/<company_ticker>')
def company(company_ticker = None):
    company = get_company_by_ticker(company_ticker)
    market_data = get_live_market_data(company_ticker)

    fundamentals = sort_fundamentals_from_company(company)
    return render_template(
        'company.html', 
        company=company, 
        fundamentals=fundamentals, 
        **market_data) #unpacking the market_data dictionary