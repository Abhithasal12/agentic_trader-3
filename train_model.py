import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from utils.indicators import add_indicators

SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M5

mt5.initialize()

rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 5000)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

df = add_indicators(df)

# Create Target
future_close = df['close'].shift(-3)
df['target'] = np.where(future_close > df['close'], 1, 0)

df.dropna(inplace=True)

features = df[['ema20','ema50','rsi']]
target = df['target']

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("Model Accuracy:", accuracy)

joblib.dump(model, "models/model.pkl")

print("Model saved successfully")
