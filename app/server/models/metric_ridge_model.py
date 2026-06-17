from app.server.database import db, Company, Report, Fundamental

from sklearn.linear_model import Ridge, Lasso, LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

import yfinance as yf
import numpy as np

model = RidgeCV(
    cv=5)

# model = LassoCV(
#     cv=5, 
#     random_state=42, 
#     positive=True) # Algorithm chooses the best alpha

scaler = StandardScaler()

def fundamental_ridge_model(): 
    features = []
    target = []

    for company in db.session.query(Company).all():
        for report in company.reports:
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
    y = np.array(np.log(target))

    test_cutoff = int(0.8 * len(X))

    X_train, X_test = X[:test_cutoff], X[test_cutoff:]
    y_train, y_test = y[:test_cutoff], y[test_cutoff:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model.fit(X_train_scaled, y_train)

    # --- Print Model Coefficients Table ---
    feature_names = [
        "Revenue", 
        #"Depreciation", 
        "EBITDA", 
        "EBIT", 
        "Net Income", 
        "Total Equity", 
        "Short Term Debt", 
        "Long Term Debt", 
        "Current Assets", 
        "Fixed Assets", 
        "Cash", 
        "Inventory", 
        "Account Receivables"
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
    log_predictions = model.predict(X_test_scaled)

    actual_y_test = np.exp(y_test)
    actual_predictions = np.exp(log_predictions)  

    r2 = r2_score(actual_y_test, actual_predictions)
    mape = mean_absolute_percentage_error(actual_y_test, actual_predictions)
    mae = mean_absolute_error(actual_y_test, actual_predictions)
    rmse = np.sqrt(mean_squared_error(actual_y_test, actual_predictions))

    # --- Print Test Evaluation Metrics Table ---
    print("="*60)
    print(f"{'Metric':<38} | {'Value'}")
    print("="*60)
    print(f"{'R-squared (R2) Score':<38} | {r2:.4f}")
    print(f"{'Mean Absolute Percentage Error (MAPE)':<38} | {mape * 100:,.2f}%")
    print(f"{'Mean Absolute Error (MAE)':<38} | {mae:,.2f}")
    print(f"{'Root Mean Squared Error (RMSE)':<38} | {rmse:,.2f}")
    print("="*60 + "\n")
