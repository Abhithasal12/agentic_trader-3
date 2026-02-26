import joblib
import pandas as pd

model = joblib.load("models/model.pkl")

def generate_signal(df):

    last = df.iloc[-1][['ema20','ema50','rsi']]
    features = pd.DataFrame([last])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    if prediction == 1 and probability > 0.6:
        return "BUY"
    else:
        return None
