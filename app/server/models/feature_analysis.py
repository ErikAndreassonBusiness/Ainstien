import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from pathlib import Path

from app.server.db_queries import build_dataframe_for_models

def get_settings(data):
    print('Data received for settings: ', data, "\n")
    return {
        "fundamental_features": data.get('fundamental_features'),
        "metric_features": data.get('metric_features'),
        "chosen_target": data.get('target_variable'),
        "log_transform_target": data.get('log_transform'), 
        "transformation_map": data.get('transformations')
    }

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


def print_diagnostics(data):
    timestamp = int(time.time())
    X, y = get_features_and_target_df(get_settings(data))

    # Prepare dataframes for the printing utilities
    df_check = X.copy()
    df_check['TARGET'] = y

    # Run printers cleanly by passing exactly what they need
    remove_past_images()
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