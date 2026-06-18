from app.server.database import db, Company, Report, Fundamental, Metric

from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

from flask import jsonify

import yfinance as yf
import numpy as np
import pandas as pd

from app.server.db_queries import (
    get_all_companies, 
    get_all_reports
)

# model = RidgeCV(
#     cv=5)

# model = LassoCV(
#     cv=5, 
#     random_state=42, 
#     positive=True) # Algorithm chooses the best alpha

scaler = StandardScaler()

def get_features_from_db(chosen_features, features):

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

def get_target_from_db(chosen_target):
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
    
def run_model(settings): 
    features = get_features_from_db(settings.get("chosen_features"), settings.get("features"))
    target = get_target_from_db(settings.get("chosen_target"))

    X = np.array(features)

    # --- Optionally log-transform the target variable ---
    if settings.get("log_transform_target") == "on":
        y = np.array(np.log(target)) 
    else:
        y = np.array(target)

    test_cutoff = int(0.8 * len(X))

    X_train, X_test = X[:test_cutoff], X[test_cutoff:]
    y_train, y_test = y[:test_cutoff], y[test_cutoff:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    performance_list = []
    coefficients_dict = {}

    for model in settings.get("chosen_models"):
        if model == "Ridge":
            model = RidgeCV(cv=settings.get("cv_folds"))
        elif model == "Lasso":
            model = LassoCV(
                cv=settings.get("cv_folds"), 
                random_state=42, 
                positive=settings.get("positive_coefficients") == "on")

        model.fit(X_train_scaled, y_train)

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

        performance_list.append({
            "model_name": model.__class__.__name__,
            "r2": round(r2, 4),
            "mape": round(mape, 4),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4)
        })

        coefficients_dict[model.__class__.__name__] = model.coef_.tolist()

        return {
            "performance": performance_list,
            "coefficients": coefficients_dict
        }

def get_correlation_matrix(data):
    attributes_to_calc = []

    for company in get_all_companies():
        for report in get_all_reports(company):
            fundamental_data = report.fundamental.to_dict()
            #metric_data = report.metric.to_dict()

            feature_row = {}
            for feature in data.get("features"):
                feature_row[feature] = fundamental_data[feature]
                #metrics = metric_data.get(feature)
                #attributes_to_calc.append(metrics)

            attributes_to_calc.append(feature_row)

    # Build correlation matrix
    df = pd.DataFrame(attributes_to_calc)  # Transpose to get features as columns
    matrix = df.corr().values.tolist()

    matrix_dict = {
        "matrix": matrix
    }
    
    return jsonify(matrix_dict)