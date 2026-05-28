from app.server.database import db, Company, Report, Fundamental
from sklearn.linear_model import Ridge, Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import numpy as np

ridge_model = Ridge(alpha=1.0)
lasso_model = Lasso(alpha=0.1, positive=True)
lassoCV_model = LassoCV(cv=5, random_state=42, positive=True)
scaler = StandardScaler()

def fundamental_model(): 
    features = []
    target = []

    for company in db.session.query(Company).all():
        for report in company.reports:
            data = report.fundamental.to_dict()
                
            feature_row = [
                    data.get("revenue"),
                    data.get("depreciation"),
                    data.get("ebitda"),
                    data.get("ebit"),
                    data.get("net_income"),
                    data.get("total_assets"),
                    data.get("total_equity"),
                    data.get("total_debt"),
                    data.get("current_assets"),
                    data.get("fixed_assets"),
                    data.get("cash"),
                    data.get("inventory"),
                    data.get("account_receiveables")
                ]
                
            features.append(feature_row)
            target.append(report.max_average_future_price * report.share_outstanding)
    
    features_scaled = scaler.fit_transform(features)
    target_scaled = np.array(target)

    test_cutoff = int(0.8 * len(features_scaled))

    lasso_model.fit(features_scaled[:test_cutoff], target_scaled[:test_cutoff])
    lassoCV_model.fit(features_scaled[:test_cutoff], target_scaled[:test_cutoff])
    print(lasso_model.coef_)
    print(lassoCV_model.coef_)
    print(lassoCV_model.alpha_)

    lasso_predictions = lasso_model.predict(features_scaled[test_cutoff:])
    lassoCV_predictions = lassoCV_model.predict(features_scaled[test_cutoff:])

    for i in range(len(features_scaled[test_cutoff:])):
        lasso = lasso_predictions[i]
        lassoCV = lassoCV_predictions[i]
        real = target[test_cutoff + i]
        print(f"Diff Lasso: {lasso/real}, Diff LassoCV: {lassoCV/real}")


