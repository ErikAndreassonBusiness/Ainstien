from app.server.db_queries import (
    get_all_companies, 
    get_all_reports
)

import pandas as pd

import pandas as pd

# ======= Run Models Extra features ========

def extract_features_from_report(report, features):
    fundamental_dict = report.fundamental.to_dict() if report.fundamental else {}
    metric_dict = report.metric.to_dict() if report.metric else {}
    
    all_data = {**fundamental_dict, **metric_dict}
    return {feat: all_data[feat] for feat in features if feat in all_data}


def get_correlation_matrix(data):
    fundamentals = data.get('features').get('fundamental_features', [])
    metrics = data.get('features').get('metric_features', [])
    all_features = fundamentals + metrics

    attributes_to_calc = []
    
    for company in get_all_companies():
        reports = get_all_reports(company)
        reports_to_process = reports if not metrics else reports[1:]
    
        for report in reports_to_process:
            feature_row = extract_features_from_report(report, all_features)
            if feature_row:  
                attributes_to_calc.append(feature_row)

    df = pd.DataFrame(attributes_to_calc)
    return {"matrix": df.corr().values.tolist()}
    

# === Target Variants ===
def get_target_names(): 
    return {
        "targets": [
            {"value": "future_price", "label_fallback": "Future Price Target"},
            {"value": "future_growth", "label_fallback": "Future Growth Target"}
    ]}
