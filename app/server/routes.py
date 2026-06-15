# app/server/routes.py
from flask import render_template, current_app as app, jsonify, redirect, url_for
from .db_queries import (
    get_all_tickers_in_order, 
    get_company_by_ticker, 
    sort_fundamentals_from_company
)
from .live_market import get_live_market_data
from .db_queries import get_dashboard_market_data, get_company_by_ticker, get_company_fundamentals_history

@app.route('/api/market-summary', methods = ['GET'])
def market_summary():
    data = get_dashboard_market_data()
    return jsonify(data)

@app.route('/api/company-details/<ticker>')
def api_company_details(ticker):
    return get_company_fundamentals_history(ticker)

@app.route('/api/market-data/<ticker>', methods = ['GET'])
def api_market_data(ticker = None):
    data = get_live_market_data(ticker)
    return jsonify(data)
    
# ===== Standard routes =======

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/run-models')
def run_models():
    return render_template('run_models.html')

@app.route('/company/<ticker>')
def company(ticker):
    return render_template('company.html', ticker=ticker)


