import MetaTrader5 as mt5
import pandas as pd
from config import CONFIG


# ------------------------------------------------------------
# Timeframe Mapping
# ------------------------------------------------------------

TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
}


# ------------------------------------------------------------
# Indicator Calculations
# ------------------------------------------------------------

def calculate_indicators(df, strategy_config):

    fast = strategy_config["fast_ema"]
    slow = strategy_config["slow_ema"]
    rsi_period = strategy_config["rsi_period"]

    df["ema_fast"] = df["close"].ewm(span=fast).mean()
    df["ema_slow"] = df["close"].ewm(span=slow).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
    loss = -delta.where(delta < 0, 0).rolling(rsi_period).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)

    return df


# ------------------------------------------------------------
# Signal Generator
# ------------------------------------------------------------

def generate_signal(symbol):

    strategy_config = CONFIG["strategy"]
    timeframe = TIMEFRAME_MAP[strategy_config["timeframe"]]

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)

    if rates is None or len(rates) < 50:
        return None

    df = pd.DataFrame(rates)
    df = calculate_indicators(df, strategy_config)

    if len(df) < 3:
        return None

    # Last two candles for crossover detection
    prev = df.iloc[-2]
    curr = df.iloc[-1]

    signal = None

    # BUY condition
    if (
        prev["ema_fast"] < prev["ema_slow"]
        and curr["ema_fast"] > curr["ema_slow"]
        and curr["rsi"] > strategy_config["rsi_buy_level"]
    ):
        signal = "buy"

    # SELL condition
    elif (
        prev["ema_fast"] > prev["ema_slow"]
        and curr["ema_fast"] < curr["ema_slow"]
        and curr["rsi"] < strategy_config["rsi_sell_level"]
    ):
        signal = "sell"

    return signal
