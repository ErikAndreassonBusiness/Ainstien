from app.server.database import db, Company
from sklearn.linear_model import Ridge, Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import numpy as np

ridge_model = Ridge(alpha=1.0)
lasso_model = Lasso(alpha=0.1, positive=True)
lassoCV_model = LassoCV(cv=5, random_state=42, positive=True)
scaler = StandardScaler()

def get_market_cap(company):
    try:
        price = yf.Ticker(company.ticker).history(start="2026-01-02", end="2026-03-02")['Close'].max() * yf.Ticker(company.ticker).info['sharesOutstanding']
        return price
    except Exception as e:
        return None

def model():
    data_list = []
    price_list = []

    for company in db.session.query(Company).all():
        price = get_market_cap(company)
        if price is not None:
            data_list.append(company.fundamentals[2].serialize_fundamental_info())
            price_list.append(price)

    data_scaled = scaler.fit_transform(data_list)
    price_scaled = np.array(price_list) / 1e6

    test_cutoff = int(0.8 * len(data_scaled))

    lasso_model.fit(data_scaled[:test_cutoff], price_scaled[:test_cutoff])
    lassoCV_model.fit(data_scaled[:test_cutoff], price_scaled[:test_cutoff])
    print(lasso_model.coef_)
    print(lassoCV_model.coef_)
    print(lassoCV_model.alpha_)

    lasso_predictions = lasso_model.predict(data_scaled[test_cutoff:])
    lassoCV_predictions = lassoCV_model.predict(data_scaled[test_cutoff:])

    for i in range(len(data_scaled[test_cutoff:])):
        lasso = lasso_predictions[i] * 1e6
        lassoCV = lassoCV_predictions[i] * 1e6
        real = price_list[test_cutoff + i]
        print(f"Diff Lasso: {lasso/real}, Diff LassoCV: {lassoCV/real}")

def print_stock_info():
    print(db.session.get(Company, 1).serialize())