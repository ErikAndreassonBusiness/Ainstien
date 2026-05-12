import joblib
import os

# runs the ML model to generate results

def get_prediction(data):
    # Get path to the model file
    model_path = os.path.join(os.path.dirname(__file__), 'model_assets/trading_model.pkl')
    model = joblib.load(model_path)
    return model.predict(data)