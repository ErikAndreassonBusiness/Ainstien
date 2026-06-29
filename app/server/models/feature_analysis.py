import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

from app.server.db_queries import build_dataframe_for_models

def get_settings(data):
    return {
        "fundamental_features": data.get('fundamental_features'),
        "metric_features": data.get('metric_features'),
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform')
    }

def get_features_and_target_df(settings):
    """
    Uses Pandas to filter columns and calculate the target variable using vectorization.
    """
    fundamental_features = settings['fundamental_features'] or []
    metric_features = settings['metric_features'] or []
    chosen_target = settings['chosen_target']

    # Build the dataframe
    df = build_dataframe_for_models(metric_features_enabled=bool(metric_features))

    if chosen_target == "future_price": 
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
    all_features = selected_fundamental + selected_metric

    # Extract features and targets
    X = df[all_features].copy()
    y = df['target'].copy()

    print("Settings log: ", settings.get('log_transform_target'))
    if settings.get("log_transform_target") == "on":
        y = np.log(y)

    return X, y

def print_target_outliers(df_check): 
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df_check['TARGET'], kde=True, ax=axes[0])
    axes[0].set_title("Target Distribution (Skewness Check)")
    
    sns.boxplot(x=df_check['TARGET'], ax=axes[1])
    axes[1].set_title("Target Boxplot (Outlier Check)")
    
    plt.tight_layout()
    plt.savefig('app/client/static/images/target_distribution.png') 
    plt.close()


def print_feature_outliers(X): 
    # Plot Outliers
    num_features = len(X.columns)
    if num_features == 0:
        print("No features selected for outlier plotting.")
        return

    fig, axes = plt.subplots(nrows=int(np.ceil(num_features/4)), ncols=4, figsize=(16, max(4, num_features)))
    axes = axes.flatten()
    
    for i, col in enumerate(X.columns):
        # FIX: Changed df_check[col] to X[col] since X is what we passed into this scope
        sns.boxplot(y=X[col], ax=axes[i])
        axes[i].set_title(col, fontsize=9)
        axes[i].set_ylabel('')
        
    # Clear unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.suptitle("Individual Feature Boxplots (Outlier Check)", fontsize=16)
    plt.tight_layout()
    plt.savefig('app/client/static/images/outliers_scaled.png') 
    plt.close()

def print_correlation_heatmap(df_check): 
    # Correlation Heatmap
    plt.figure(figsize=(14, 12))  
    correlation_matrix = df_check.corr() 
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    
    sns.heatmap(
        correlation_matrix, 
        mask=mask,
        annot=True,            
        cmap='coolwarm', 
        fmt=".2f", 
        linewidths=0.5,
        cbar_kws={"shrink": .8}
    )
    plt.title("Linear Correlation Heatmap (Features vs Target)")
    plt.tight_layout()
    plt.savefig('app/client/static/images/correlation_matrix.png')
    plt.close()


def print_diagnostics(data):
    X, y = get_features_and_target_df(get_settings(data))

    # Prepare dataframes for the printing utilities
    df_check = X.copy()
    df_check['TARGET'] = y

    # Run printers cleanly by passing exactly what they need
    print_target_outliers(df_check)
    print_feature_outliers(X)
    print_correlation_heatmap(df_check)

    timestamp = int(time.time())
    
    return {
        "status": "success", 
        "images": {
            "target_distribution": f"/static/images/target_distribution.png?v={timestamp}",
            "outliers_scaled": f"/static/images/outliers_scaled.png?v={timestamp}",
            "correlation_matrix": f"/static/images/correlation_matrix.png?v={timestamp}"
        }
    }