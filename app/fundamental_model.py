from app.server.database import db, Company, Report, Fundamental
from sklearn.linear_model import Ridge, Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import numpy as np

#ridge_model = Ridge(alpha=1.0) not used
lassoCV_model = LassoCV(
    cv=5, 
    random_state=42, 
    positive=True) # Algorithm chooses the best alpha

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

    lassoCV_model.fit(
        features_scaled[:test_cutoff], 
        target_scaled[:test_cutoff]) #5 -fold automatically
    
    #Print betas
    print("Revenue: ",                lassoCV_model.coef_[0])
    print("Depreciation: ",           lassoCV_model.coef_[1])
    print("EBITDA: ",                 lassoCV_model.coef_[2])
    print("EBIT: ",                   lassoCV_model.coef_[3])
    print("Net Income: ",             lassoCV_model.coef_[4])
    print("Total Assets: ",           lassoCV_model.coef_[5])
    print("Total Equity: ",           lassoCV_model.coef_[6])
    print("Total Debt: ",             lassoCV_model.coef_[7])
    print("Current Assets: ",         lassoCV_model.coef_[8])
    print("Fixed Assets: ",           lassoCV_model.coef_[9])
    print("Cash: ",                   lassoCV_model.coef_[10])
    print("Inventory: ",              lassoCV_model.coef_[11])
    print("Account Receivables: ",    lassoCV_model.coef_[12])

    #print(lasso_model.coef_)
    #print(lassoCV_model.coef_)
    print("\n")
    print("Winning alpha: ", lassoCV_model.alpha_)
    print("\n")

    #lasso_predictions = lasso_model.predict(features_scaled[test_cutoff:])
    lassoCV_predictions = lassoCV_model.predict(features_scaled[test_cutoff:])

    sum = 0
    for i in range(len(features_scaled[test_cutoff:])):
        #lasso = lasso_predictions[i]
        lassoCV = lassoCV_predictions[i]
        real = target[test_cutoff + i]
        print(f"Diff LassoCV: {round((lassoCV/real), 2)} %")
        sum = sum + round((lassoCV/real), 2)

    print("\n")
    print("Avarage prediction. ", round(sum / len(features_scaled[test_cutoff:]), 2), "%")
    print("\n")


