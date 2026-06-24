from app.server.database import db, Company, Report, Fundamental, Metric

from sklearn.linear_model import LassoCV, RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

from flask import jsonify

import yfinance as yf
import numpy as np
import pandas as pd

from app.server.db_queries import (
    get_all_companies, 
    get_all_reports, 
    get_metrics_attrbiute_names
)

def get_target_from_db(report, chosen_target):
    if chosen_target == "future_price":
        return report.max_average_future_price * report.share_outstanding

    elif chosen_target == "future_growth":
        return (report.max_average_future_price / report.current_price - 1) * 100

# =============
def get_features_and_target(settings):
    features = []
    targets = []
    
    chosen_features = settings.get("chosen_features")
    print("Amount of features: ", len(chosen_features))
    chosen_target = settings.get("chosen_target")
    contains_metrics = settings.get("contains_metrics")

    for company in get_all_companies():
        reports = get_all_reports(company)
        reports_to_process = reports[1:] if contains_metrics else reports

        for report in reports_to_process:
            target = get_target_from_db(report, chosen_target)

            report_features = []
            for feature in chosen_features:
                if hasattr(report.fundamental, feature):
                    report_features.append(getattr(report.fundamental, feature))

                elif contains_metrics and hasattr(report.metric, feature):
                    report_features.append(getattr(report.metric, feature))

                else: 
                    print(report.id)
                    print("Missing feature: ", feature, "\n")

            features.append(report_features)
            targets.append(target)

    return features, targets

#==========
def log_target(log_transform, target):
    # --- Optionally log-transform the target variable ---
    if log_transform == "on":
        return np.log(target)
    else:
        return target

def split_data(X, y, settings):
    split = settings.get("split")
    test_cutoff = int(float(split)*len(X))

    X_train, X_test = X[:test_cutoff], X[test_cutoff:]
    y_train, y_test = y[:test_cutoff], y[test_cutoff:]

    return X_train, X_test, y_train, y_test

def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled

def choose_model(chosen_model, settings): 
    if chosen_model == "ridge":
        model = RidgeCV(cv=int(settings.get("cv_folds")))

    elif chosen_model == "lasso":
        model = LassoCV(
            cv=int(settings.get("cv_folds")), 
            random_state=42, 
            positive=True if settings.get('positive_coef') == "on" else False)
    
    elif chosen_model == "elasticnet": 
        model = ElasticNetCV(
            l1_ratio=0.5, #change to dynamic
            cv = int(settings.get("cv_folds")), 
            random_state=42, 
            positive=True if settings.get('positive_coef') == "on" else False)

    return model

def exp_y_from_log(settings, y_test, predictions): 
    if settings.get("log_transform_target") == "on":
            actual_y_test = np.exp(y_test)
            actual_predictions = np.exp(predictions)

    else:
        actual_y_test = y_test
        actual_predictions = predictions

    return actual_y_test, actual_predictions

def calc_errors(actual_y_test, actual_predictions): 
    r2 = r2_score(actual_y_test, actual_predictions)
    mape = mean_absolute_percentage_error(actual_y_test, actual_predictions)
    mae = mean_absolute_error(actual_y_test, actual_predictions)
    rmse = np.sqrt(mean_squared_error(actual_y_test, actual_predictions))

    return r2, mape, mae, rmse

def get_settings(data):
    chosen_features = data.get('features')
    all_metrics = get_metrics_attrbiute_names()

    return {
        "chosen_models": data.get('models'),
        "chosen_features": chosen_features,
        "contains_metrics": not set(chosen_features).isdisjoint(all_metrics), #True if overlapps
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform'),
        "cv_folds": data.get('cv_folds'), 
        "positive_coef": data.get('positive_coefficients'),
        "split": data.get('test_split'), 
    }

def config_data(settings, features, target):
    # --- Define X and y ---
    X = np.array(features)
    print("My X: ", X.shape)
    y = log_target(settings.get("log_transform_target"), target)

    # --- Split data sets ---
    X_train, X_test, y_train, y_test = split_data(X, y, settings)

    #--- Scale features ---
    X_train_scaled, X_test_scaled = scale_features(X_train, X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test

def calc_all_models(settings, X_train_scaled, X_test_scaled, y_train, y_test): 
    performance_list = []
    coefficients_dict = {}

    for chosen_model in settings.get("chosen_models"):
        model = choose_model(chosen_model, settings)
        model.fit(X_train_scaled, y_train)

        # --- Make predicitons and calc errors
        actual_y_test, actual_prediction = exp_y_from_log(
            settings=settings, 
            y_test=y_test, 
            predictions=model.predict(X_test_scaled))

        r2, mape, mae, rmse = calc_errors(actual_y_test, actual_prediction)

        # --- Return in JSON ---
        performance_list.append({
            "model_name": model.__class__.__name__,
            "r2": round(r2, 2),
            "mape": round(mape, 2),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2)
        })

        coefficients_dict[model.__class__.__name__] = model.coef_.tolist()

    return performance_list, coefficients_dict

def run_models(data): 
    print(data)
    settings = get_settings(data)

    # --- Feature and Target selection ---
    features, target = get_features_and_target(settings=settings)

    X_train_scaled, X_test_scaled, y_train, y_test = config_data(
        settings=settings, 
        features=features, 
        target=target)

    performance_list, coefficients_dict = calc_all_models(
        settings=settings, 
        X_train_scaled=X_train_scaled, 
        X_test_scaled=X_test_scaled,
        y_train=y_train, 
        y_test=y_test)

    return {
        "performance": performance_list,
        "coefficients": coefficients_dict
    }
