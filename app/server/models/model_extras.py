from app.server.db_queries import (
    get_all_companies, 
    get_all_reports
)

import pandas as pd

# ======= Run Models Extra features ========
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
