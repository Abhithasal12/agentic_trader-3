import MetaTrader5 as mt5
import pandas as pd


# ===============================
# DATA FETCH
# ===============================

def get_data(symbol, timeframe, bars=300):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df


# ===============================
# SWING DETECTION
# ===============================

def detect_swings(df, lookback=2):
    swing_highs = []
    swing_lows = []

    for i in range(lookback, len(df) - lookback):
        current_high = df['high'].iloc[i]
        current_low = df['low'].iloc[i]

        if current_high == max(df['high'].iloc[i-lookback:i+lookback+1]):
            swing_highs.append((i, current_high))

        if current_low == min(df['low'].iloc[i-lookback:i+lookback+1]):
            swing_lows.append((i, current_low))

    return swing_highs, swing_lows


# ===============================
# BREAK OF STRUCTURE (BOS)
# ===============================

def detect_bos(df, swing_highs, swing_lows):
    if not swing_highs or not swing_lows:
        return None

    last_close = df['close'].iloc[-1]

    last_swing_high = swing_highs[-1][1]
    last_swing_low = swing_lows[-1][1]

    if last_close > last_swing_high:
        return "bullish_bos"

    if last_close < last_swing_low:
        return "bearish_bos"

    return None


# ===============================
# LIQUIDITY SWEEP
# ===============================

def detect_liquidity_sweep(df, swing_highs, swing_lows):
    if not swing_highs or not swing_lows:
        return None

    last_candle = df.iloc[-1]

    last_swing_high = swing_highs[-1][1]
    last_swing_low = swing_lows[-1][1]

    # Sweep above highs then close below
    if last_candle['high'] > last_swing_high and last_candle['close'] < last_swing_high:
        return "buy_side_liquidity_swept"

    # Sweep below lows then close above
    if last_candle['low'] < last_swing_low and last_candle['close'] > last_swing_low:
        return "sell_side_liquidity_swept"

    return None


# ===============================
# FAIR VALUE GAP (FVG)
# ===============================

def detect_fvg(df):
    fvg_zones = []

    for i in range(2, len(df)):
        high_1 = df['high'].iloc[i-2]
        low_1 = df['low'].iloc[i-2]

        high_3 = df['high'].iloc[i]
        low_3 = df['low'].iloc[i]

        # Bullish FVG
        if low_3 > high_1:
            fvg_zones.append({
                "type": "bullish",
                "low": high_1,
                "high": low_3,
                "index": i
            })

        # Bearish FVG
        if high_3 < low_1:
            fvg_zones.append({
                "type": "bearish",
                "low": high_3,
                "high": low_1,
                "index": i
            })

    return fvg_zones

# ===============================
# ORDER BLOCK DETECTION
# ===============================

def detect_order_block(df, direction):
    """
    For bullish:
        Last bearish candle before bullish BOS impulse
    For bearish:
        Last bullish candle before bearish BOS impulse
    """

    if len(df) < 5:
        return None

    # Look back for last opposite candle
    for i in range(len(df)-2, 2, -1):

        open_price = df['open'].iloc[i]
        close_price = df['close'].iloc[i]

        # Bullish OB → last bearish candle
        if direction == "bullish" and close_price < open_price:
            return {
                "type": "bullish",
                "low": df['low'].iloc[i],
                "high": df['high'].iloc[i],
                "index": i
            }

        # Bearish OB → last bullish candle
        if direction == "bearish" and close_price > open_price:
            return {
                "type": "bearish",
                "low": df['low'].iloc[i],
                "high": df['high'].iloc[i],
                "index": i
            }

    return None