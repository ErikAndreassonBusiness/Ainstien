from app.server.db_queries import (
    get_all_companies, 
    get_all_reports
)

import pandas as pd
from scipy import stats

# ======= Run Models Extra features ========

def extract_features_from_report(report, features):
    fundamental_dict = report.fundamental.to_dict() if report.fundamental else {}
    metric_dict = report.metric.to_dict() if report.metric else {}
    
    all_data = {**fundamental_dict, **metric_dict}
    return {feat: all_data[feat] for feat in features if feat in all_data}


def get_correlation_matrix(data):
    fundamentals = data.get('data_to_get').get('fundamental_features', [])
    metrics = data.get('data_to_get').get('metric_features', [])
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
            {"value": "future_max_price", "label_fallback": "Future Price Target"},
            {"value": "future_growth", "label_fallback": "Future Growth Target"}
    ]}

# === See Company Outliers ===
def compute_database_zscores(target_variable="future_max_price"):
    """
    Queries all companies and reports, flattens the financial data,
    and computes Z-scores to isolate extreme outlier entries.
    """
    records = []
    
    all_companies = get_all_companies()
    
    for company in all_companies:
        for report in get_all_reports(company):
            
            if target_variable == "future_price":
                target_value = report.max_average_future_price * report.share_outstanding
            elif target_variable == "future_growth":
                target_value = (report.max_average_future_price / report.current_price - 1) * 100

            row = {
                "company_ticker": company.ticker,
                "company_name": company.name,
                "report_date": report.report_date,
                "target_value": target_value
            }
            
            # Safely merge raw fundamental values if present
            if report.fundamental:
                row.update(report.fundamental.to_dict())
                
            records.append(row)
            
    df = pd.DataFrame(records)
    
    df['target_zscore'] = stats.zscore(df['target_value'])
    df['revenue_zscore'] = stats.zscore(df['revenue']) if 'revenue' in df.columns else 0
    df['assets_zscore'] = stats.zscore(df['total_assets']) if 'total_assets' in df.columns else 0

    return df

def print_outlier_summary(df, threshold=3.0):
    """Filters and prints records that cross your outlier boundary limit."""
        
    print(f"=== HOUNDING OUTLIERS crossing |Z| > {threshold} ===")
    
    # Isolate targets that deviate too drastically from normal bounds
    outliers = df[df['target_zscore'].abs() > threshold]
    
    if outliers.empty:
        print("No extreme deviations identified in target scales.")
    else:
        for idx, row in outliers.sort_values(by='target_zscore', ascending=False).iterrows():
            print(f"[{row['company_ticker']}] {row['company_name']} ({row['report_date']})")
            print(f"  -> Raw Value: {row['target_value']:,.2f}")
            print(f"  -> Z-Score:   {row['target_zscore']:.2f} Standard Deviations away\n")