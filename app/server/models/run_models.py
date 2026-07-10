from sklearn.linear_model import LassoCV, RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') #To plot at the same time with Flask
import seaborn as sns
import matplotlib.pyplot as plt

from app.server.db_queries import (
    get_all_companies, 
    get_all_reports, 
    get_all_fundamentals, 
    get_all_metrics,
    build_dataframe_for_models,
    get_metrics_attrbiute_names
)

from .data_functions import get_features_and_target_df

def get_settings(data):
    print("Data: ", data)
    return {
        "chosen_models": data.get('models'),
        "fundamental_features": data.get('fundamental_features'),
        "metric_features": data.get('metric_features'),
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform'),
        "cv_folds": data.get('cv_folds'), 
        "positive_coef": data.get('positive_coefficients'),
        "split": data.get('test_split'), 
        "transformation_map": data.get('transformations')
    }

def split_data(X, y, settings):
    split = float(settings.get("split"))
    test_cutoff = int(split * len(X))

    X_train, X_test = X.iloc[:test_cutoff], X.iloc[test_cutoff:]
    y_train, y_test = y.iloc[:test_cutoff], y.iloc[test_cutoff:]

    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled


def choose_model(chosen_model, settings): 
    cv_folds = int(settings.get("cv_folds"))
    is_positive = settings.get('positive_coef') == "on"

    if chosen_model == "ridge":
        return RidgeCV(cv=cv_folds)
    elif chosen_model == "lasso":
        return LassoCV(cv=cv_folds, random_state=42, positive=is_positive)
    elif chosen_model == "elasticnet": 
        return ElasticNetCV(l1_ratio=0.5, cv=cv_folds, random_state=42, positive=is_positive)


def exp_y_from_log(settings, y_test, predictions): 
    if settings.get("log_transform_target") == "on":
        return np.exp(y_test), np.exp(predictions)
    return y_test, predictions


def calc_errors(actual_y_test, actual_predictions): 
    return (
        r2_score(actual_y_test, actual_predictions),
        mean_absolute_percentage_error(actual_y_test, actual_predictions),
        mean_absolute_error(actual_y_test, actual_predictions),
        np.sqrt(mean_squared_error(actual_y_test, actual_predictions))
    )

def print_baseline(y_train): 
    y_mean = np.mean(y_train)
    y_prediction_baseline = [y_mean] * len(y_train)
    MAE_baseline = mean_absolute_error(y_train, y_prediction_baseline)

    print("Mean Y:", round(y_mean, 2))
    print("Baseline MAE:", round(MAE_baseline, 2)) 


def calc_all_models(settings, X_train_scaled, X_test_scaled, y_train, y_test): 
    performance_list = []
    coefficients_dict = {}

    for chosen_model in settings.get("chosen_models"):
        model = choose_model(chosen_model, settings)
        model.fit(X_train_scaled, y_train)

        actual_y_test, actual_prediction = exp_y_from_log(
            settings=settings, 
            y_test=y_test, 
            predictions=model.predict(X_test_scaled)
        )

        r2, mape, mae, rmse = calc_errors(actual_y_test, actual_prediction)

        performance_list.append({
            "model_name": model.__class__.__name__,
            "r2": round(r2, 2),
            "mape": round(mape, 2),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2)
        })

        coefficients_dict[model.__class__.__name__] = model.coef_.tolist()

    return performance_list, coefficients_dict


#
# --- Main functiion ---
#
def run_models(data): 
    settings = get_settings(data)

    # Handle data
    X, y = get_features_and_target_df(settings=settings)
    X_train, X_test, y_train, y_test = split_data(X, y, settings)
    X_train_scaled, X_test_scaled = scale_features(X_train, X_test)
    
    print_baseline(y_train)

    # Train and Evaluate
    performance_list, coefficients_dict = calc_all_models(
        settings=settings, 
        X_train_scaled=X_train_scaled, 
        X_test_scaled=X_test_scaled,
        y_train=y_train, 
        y_test=y_test
    )

    return {
        "performance": performance_list,
        "coefficients": coefficients_dict
    }