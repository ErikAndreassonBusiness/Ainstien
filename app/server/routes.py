# app/server/routes.py
from flask import render_template, current_app as app, jsonify, redirect, url_for
from .db_queries import (
    get_all_tickers_in_order, 
    get_company_by_ticker, 
    sort_fundamentals_from_company
)
from .live_market import get_live_market_data
from .db_queries import get_dashboard_market_data, get_company_by_ticker, get_company_fundamentals_history

# ========== API routes ============

# --- Dashboard Page---
@app.route('/api/market-summary', methods = ['GET'])
def market_summary():
    data = get_dashboard_market_data()
    return jsonify(data)

# --- Company Page ---
@app.route('/api/company-details/<ticker>')
def api_company_details(ticker):
    return get_company_fundamentals_history(ticker)

@app.route('/api/market-data/<ticker>', methods = ['GET'])
def api_market_data(ticker = None):
    data = get_live_market_data(ticker)
    return jsonify(data)
    
# --- Run Models Page ---
@app.route('/api/correlation-matrix', methods = ['POST'])
def correlation_matrix():
    data = request.get_json()
    return get_correlation_matrix(data)

@app.route('/api/run-models', methods = ['POST'])
def run_models():
    data = request.get_json()
    settings = {
        "chosen_models": data.get('models'),
        "chosen_features": data.get('features'),
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform'),
        "cv_folds": data.get('cv_folds'), 
        "positive_coefficients": data.get('positive_coefficients')
    }
    
    return jsonify(run_model(settings))
# ===== Standard routes =======

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/models')
def run_models_page():
    return render_template('run_models.html')

@app.route('/company/<ticker>')
def company(ticker):
    return render_template('company.html', ticker=ticker)


