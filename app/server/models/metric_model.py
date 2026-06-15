from app.server.database import db, Company, Report, Fundamental

from sklearn.linear_model import Ridge, Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

import yfinance as yf
import numpy as np

#model = Ridge(alpha=1.0) 
model = LassoCV(
    cv=5, 
    random_state=42) # Algorithm chooses the best alpha

scaler = StandardScaler()

def metric_model(): 
    features = []
    target = []

    for company in db.session.query(Company).all():
        for report in company.reports:
            if report.metric: 
                data = report.metric.to_dict()
                    
                feature_row = [
                        data.get("revenue_growth_percent"),
                        data.get("profit_growth_percent"),
                        data.get("quick_ratio_percent"),
                        data.get("net_debt_ebitda_ratio"),
                        data.get("equity_ratio_percent"),
                        data.get("assets_turnover_ratio"),
                        data.get("inventory_turnover_ratio"),
                        data.get("roa"),  
                        data.get("roe"), 
                        data.get("roi"), 
                        data.get("ebit_margin_percent"),
                        data.get("profit_margin_percent")
                    ]
                    
                features.append(feature_row)
                target.append((report.max_average_future_price / report.current_price - 1) * 100) #future growth in %s
    
    X = np.array(features)
    y = np.array(target)

    # Mix up the rows so train/test sets have a mix of all companies
    indices = np.arange(X.shape[0])
    np.random.seed(42)
    np.random.shuffle(indices)
    X, y = X[indices], y[indices]

    test_cutoff = int(0.8 * len(X))

    X_train, X_test = X[:test_cutoff], X[test_cutoff:]
    y_train, y_test = y[:test_cutoff], y[test_cutoff:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model.fit(X_train_scaled, y_train)

    # --- Print Model Coefficients Table ---
    feature_names = [
        "Revenue Gworth (%)", 
        "Profit Growth (%)",
        "Quick Ratio (%)",
        "Net Debt / EBITDA Ratio",
        "Equity Ratio (%)",
        "Assets Turnover Ratio",
        "Inventory Turnover Ratio",
        "ROA",
        "ROE",
        "ROI",
        "EBIT Margin (%)",
        "Profit Margin (%)"
    ]
    
    print("\n" + "="*43)
    print(f"{'Feature':<25} | {'Coefficient'}")
    print("="*43)
    
    for name, coef in zip(feature_names, model.coef_):
        coef_str = f"{coef:,.4f}" if coef != 0 else "0.00"
        print(f"{name:<25} | {coef_str}")
        
    print("="*43)
    print(f"Winning alpha: {model.alpha_:,.4f}\n")

    # --- Compare against test data ---
    predictions = model.predict(X_test_scaled)

    r2 = r2_score(y_test, predictions)
    mape = mean_absolute_percentage_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # --- Print Test Evaluation Metrics Table ---
    print("="*60)
    print(f"{'Metric':<38} | {'Value'}")
    print("="*60)
    print(f"{'R-squared (R2) Score':<38} | {r2:.4f}")
    print(f"{'Mean Absolute Percentage Error (MAPE)':<38} | {mape * 100:,.2f}%")
    print(f"{'Mean Absolute Error (MAE)':<38} | {mae:,.2f}")
    print(f"{'Root Mean Squared Error (RMSE)':<38} | {rmse:,.2f}")
    print("="*60 + "\n")