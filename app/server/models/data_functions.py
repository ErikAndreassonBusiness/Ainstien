import pandas as pd
import numpy as np

from app.server.db_queries import build_dataframe_for_models


def get_features_and_target_df(settings):
    """
    Uses Pandas to filter columns and calculate the target variable using vectorization.
    """
    print('Settings: ', settings)
    fundamental_features = settings['fundamental_features'] or []
    metric_features = settings['metric_features'] or []
    chosen_target = settings['chosen_target']
    transformation_map = settings.get('transformation_map') or {}

    # Build the dataframe
    df = build_dataframe_for_models(metric_features_enabled=bool(metric_features))

    if chosen_target == "future_max_price": 
        df['target'] = df['max_average_future_price'] * df['share_outstanding']
    elif chosen_target == "future_growth":
        df['target'] = (df['max_average_future_price'] / df['current_price'] - 1) * 100
    elif chosen_target == "one_month_price":
        df['target'] = df['one_month_price'] * df['share_outstanding']
    elif chosen_target == "two_month_price":
        df['target'] = df['two_month_price'] * df['share_outstanding']
    elif chosen_target == "three_month_price":
        df['target'] = df['three_month_price'] * df['share_outstanding']

    # Map features 
    selected_fundamental = [f"fundamental_{f}" for f in fundamental_features if f"fundamental_{f}" in df.columns]
    selected_metric = [f"metric_{m}" for m in metric_features if f"metric_{m}" in df.columns]
    all_features = []

    for base_feature in selected_fundamental + selected_metric:
        raw_feature_name = base_feature.replace("fundamental_", "").replace("metric_", "")
        transformation = transformation_map.get(raw_feature_name, "none")
        
        if transformation == "log":
            if (df[base_feature] <= 0).any(): 
                raise ValueError(f"Cannot apply log transformation to feature '{base_feature}' because it contains zero values.")
            
            new_feature_name = f"log_{base_feature}"
            df[new_feature_name] = np.log(df[base_feature])
            all_features.append(new_feature_name)

        elif transformation == "square":
            new_feature_name = f"square_{base_feature}"
            df[new_feature_name] = df[base_feature] ** 2 
            all_features.append(new_feature_name)

        elif transformation == "sqrt":
            new_feature_name = f"sqrt_{base_feature}"
            df[new_feature_name] = np.sqrt(df[base_feature])
            all_features.append(new_feature_name)
            
        elif transformation == "inverse":
            if (df[base_feature] <= 0).any(): 
                raise ValueError(f"Cannot apply inverse transformation to feature '{base_feature}' because it contains zero or negative values.")
            
            new_feature_name = f"inverse_{base_feature}"
            df[new_feature_name] = 1 / df[base_feature]
            all_features.append(new_feature_name)
            
        else:
            all_features.append(base_feature)

    # Extract features and targets
    X = df[all_features].copy()
    y = df['target'].copy()

    if settings.get("log_transform_target") == "on":
        y = np.log(y)

    return X, y
