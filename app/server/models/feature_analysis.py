import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from pathlib import Path

from app.server.db_queries import build_dataframe_for_models

from .data_functions import get_features_and_target_df

def get_settings(data):
    return {
        "fundamental_features": data.get('fundamental_features'),
        "metric_features": data.get('metric_features'),
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform'), 
        "transformation_map": data.get('transformations')
    }

# === Target Variants ===
def get_target_names(): 
    return {
        "targets": [
            {"value": "future_max_price", "label_fallback": "Future Price Target"},
            {"value": "future_growth", "label_fallback": "Future Growth Target"}
    ]}

def print_data_summary(X, y):
    df_check = X.copy()
    df_check['TARGET'] = y

    print("--- DATA SUMMARY ---")
    print(df_check.describe())

def remove_past_images():
    current_dir = Path(__file__).resolve().parent
    folderPath = current_dir.parents[1] / "client" / "static" / "images" #Go to folder
    filesList = list(folderPath.rglob("*"))

    for file in filesList:
        file.unlink()  # Remove the file

def print_target_outliers(df_check, timestamp): 
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df_check['TARGET'], kde=True, ax=axes[0])
    axes[0].set_title("Target Distribution (Skewness Check)")
    
    sns.boxplot(x=df_check['TARGET'], ax=axes[1])
    axes[1].set_title("Target Boxplot (Outlier Check)")
    
    plt.tight_layout()
    plt.savefig(f"app/client/static/images/target_distribution{timestamp}.png") 
    plt.close()
    

def print_feature_outliers(X, timestamp): 
    # Plot Outliers
    num_features = len(X.columns)
    if num_features == 0:
        return

    fig, axes = plt.subplots(
        nrows=int(np.ceil(num_features/4)), 
        ncols=4, 
        figsize=(16, max(4, num_features)))

    axes = axes.flatten()
    
    for i, col in enumerate(X.columns):
        sns.boxplot(y=X[col], ax=axes[i])
        axes[i].set_title(col, fontsize=9)
        axes[i].set_ylabel('')
        
    # Clear unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.suptitle("Outliers in Scaled Features", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"app/client/static/images/outliers_scaled{timestamp}.png") 
    plt.close()


def print_feature_target_plot(X, y, timestamp): 
    # Feature vs Target Plots
    num_features = len(X.columns)
    if num_features == 0:
        return

    fig, axes = plt.subplots(
        nrows=int(np.ceil(num_features/4)), 
        ncols=4, 
        figsize=(16, max(4, num_features)))
    axes = axes.flatten()
    
    for i, col in enumerate(X.columns):
        sns.scatterplot(x=X[col], y=y, ax=axes[i])
        axes[i].set_title(f"{col} vs Target", fontsize=9)
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Target')
        
    # Clear unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.suptitle("Feature vs Target Scatter Plots", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"app/client/static/images/feature_target_plots{timestamp}.png") 
    plt.close()
    

def print_correlation_heatmap(df_check, timestamp): 
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
    plt.savefig(f"app/client/static/images/correlation_matrix{timestamp}.png")
    plt.close()

#
# --- Main function ---
#
def print_diagnostics(data):
    timestamp = int(time.time())
    X, y = get_features_and_target_df(get_settings(data))

    # Prepare dataframes for the printing utilities
    df_check = X.copy()
    df_check['TARGET'] = y

    # Run printers cleanly by passing exactly what they need
    remove_past_images()
    print_data_summary(X, y)
    print_target_outliers(df_check, timestamp)
    print_feature_outliers(X, timestamp)
    print_correlation_heatmap(df_check, timestamp)
    print_feature_target_plot(X, y, timestamp)
    

    return {
        "status": "success", 
        "images": {
            "target_distribution": f"/static/images/target_distribution{timestamp}.png",
            "outliers_scaled": f"/static/images/outliers_scaled{timestamp}.png",
            "correlation_matrix": f"/static/images/correlation_matrix{timestamp}.png", 
            "feature_target_plots": f"/static/images/feature_target_plots{timestamp}.png"
        }
    }