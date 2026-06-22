from app.server.db_queries import (
    get_all_companies, 
    get_all_reports
)

import pandas as pd

# ======= Run Models Extra features ========
def select_features(report, attributes_to_calc, fundamentals, metrics):
    fundamental_data = report.fundamental.to_dict()
    metric_data = report.metric.to_dict()

    feature_row = {}
    for feature in fundamentals + metrics:
        if feature in fundamental_data:
            feature_row[feature] = fundamental_data[feature]

        elif feature in metric_data:
            feature_row[feature] = metric_data[feature]

        attributes_to_calc.append(feature_row)

def get_correlation_matrix(data):
    print("Data: ", data)
    fundamentals = data.get('fundamental_features', [])
    metrics = data.get('metric_features', [])

    attributes_to_calc = []
    for company in get_all_companies():

        if metrics is None: 
            for report in get_all_reports(company):
                select_features(
                    report=report, 
                    attributes_to_calc=attributes_to_calc, 
                    fundamentals=fundamentals, 
                    metrics=metrics)
        else: 
            for report in get_all_reports(company)[1:]:
                select_features(
                    report=report, 
                    attributes_to_calc=attributes_to_calc, 
                    fundamentals=fundamentals, 
                    metrics=metrics)


    # Build correlation matrix
    df = pd.DataFrame(attributes_to_calc)  # Transpose to get features as columns
    matrix = df.corr().values.tolist()

    return {
        "matrix": matrix
    }
    


# === Target Variants ===
def get_target_names(): 
    return {
        "targets": [
            {"value": "future_price", "label_fallback": "Future Price Target"},
            {"value": "future_growth", "label_fallback": "Future Growth Target"}
    ]}
