from app.server.database import db, Company, Report, Fundamental, Metric

from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

import yfinance as yf
import numpy as np

# model = RidgeCV(
#     cv=5)

# model = LassoCV(
#     cv=5, 
#     random_state=42, 
#     positive=True) # Algorithm chooses the best alpha

scaler = StandardScaler()

def get_features(chosen_features, features):

    # --- Build feature matrix vector ---
    features = []
    for company in db.session.query(Company).all():
        for report in company.reports:

            fundamental_data = report.fundamental.to_dict()
            for feature in chosen_features:
                features.append(fundamental_data.get(feature))
            
            metric_data = report.metric.to_dict()
            for feature in chosen_features:
                features.append(metric_data.get(feature))
    
    return features

def get_target(chosen_target):
    # --- Build target vector --
    targets = []
    if chosen_target == "future_price":
        for company in db.session.query(Company).all():
            for report in company.reports:
                targets.append(report.max_average_future_price * report.share_outstanding)

    elif chosen_target == "future_growth":
        for company in db.session.query(Company).all():
            for report in company.reports:
                targets.append((report.max_average_future_price / report.current_price - 1) * 100)

    return targets
    
    
def run_model(chosen_features, chosen_target, settings): 
    features = get_features(chosen_features)
    target = get_target(chosen_target)

    X = np.array(features)

    # --- Optionally log-transform the target variable ---
    if settings.get("log_transform_target"):
        y = np.array(np.log(target)) #great to do when the target vaires a lot //Erik
    else:
        y = np.array(target)

    test_cutoff = int(0.8 * len(X))

    X_train, X_test = X[:test_cutoff], X[test_cutoff:]
    y_train, y_test = y[:test_cutoff], y[test_cutoff:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model.fit(X_train_scaled, y_train)
    
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

    actual_y_test = np.exp(y_test)

    if settings.get("log_transform_target"):
        actual_predictions = np.exp(predictions)
    else:
        actual_predictions = predictions

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