# app/server/routes.py
from flask import (
    render_template, 
    current_app as app, 
    jsonify, 
    redirect, 
    url_for, 
    request
)

from .live_market import get_live_market_data

from .db_queries import (
    get_dashboard_market_data, 
    get_company_fundamentals_history, 
    get_fundamentals_attrbiute_names, 
    get_metrics_attrbiute_names, 
    get_metrics_attrbiute_names
)

from .models.run_models import (
    run_models, 
    get_correlation_matrix
)

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
    return get_correlation_matrix(request.get_json())

@app.route('/api/run-models', methods = ['POST'])
def model():
    return jsonify(run_models(request.get_json()))

@app.route('/api/feature-names', methods = ['GET'])
def feature_names():
    return jsonify({
        "fundamental_features": get_fundamentals_attrbiute_names(),
        "metric_features": get_metrics_attrbiute_names()
    })

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


