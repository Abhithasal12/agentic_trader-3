import MetaTrader5 as mt5
import time
from config import CONFIG
from strategy import generate_signal
from risk import calculate_lot, check_margin
from smc_logic import *
from trade_manager import (
    TradeTracker,
    has_open_position,
    check_global_limits,
    check_symbol_limits,
    send_order
)

# ------------------------------------------------------------
# MT5 CONNECTION
# ------------------------------------------------------------

def connect_mt5():
    if not mt5.initialize():
        print("MT5 initialization failed")
        quit()
    print("Connected to MT5")


# ------------------------------------------------------------
# MAIN ENGINE
# ------------------------------------------------------------
def smc_analysis(symbol):

    # ===============================
    # H4 BIAS
    # ===============================
    df_h4 = get_data(symbol, mt5.TIMEFRAME_H4, 300)
    swing_highs_h4, swing_lows_h4 = detect_swings(df_h4)
    bos_h4 = detect_bos(df_h4, swing_highs_h4, swing_lows_h4)

    if bos_h4 == "bullish_bos":
        bias = "bullish"
    elif bos_h4 == "bearish_bos":
        bias = "bearish"
    else:
        return None

    # ===============================
    # M15 SETUP + ORDER BLOCK
    # ===============================
    df_m15 = get_data(symbol, mt5.TIMEFRAME_M15, 300)
    swing_highs_m15, swing_lows_m15 = detect_swings(df_m15)

    sweep_m15 = detect_liquidity_sweep(df_m15, swing_highs_m15, swing_lows_m15)
    bos_m15 = detect_bos(df_m15, swing_highs_m15, swing_lows_m15)

    if bias == "bullish":
        if sweep_m15 != "sell_side_liquidity_swept":
            return None
        if bos_m15 != "bullish_bos":
            return None

        ob = detect_order_block(df_m15, "bullish")
        if ob is None:
            return None

        # price must retrace into OB
        current_price_m15 = df_m15['close'].iloc[-1]
        if not (ob["low"] <= current_price_m15 <= ob["high"]):
            return None

        direction = "buy"

    elif bias == "bearish":
        if sweep_m15 != "buy_side_liquidity_swept":
            return None
        if bos_m15 != "bearish_bos":
            return None

        ob = detect_order_block(df_m15, "bearish")
        if ob is None:
            return None

        current_price_m15 = df_m15['close'].iloc[-1]
        if not (ob["low"] <= current_price_m15 <= ob["high"]):
            return None

        direction = "sell"
        
    # ===============================
    # M5 STRUCTURE
    # ===============================
    df_m5 = get_data(symbol, mt5.TIMEFRAME_M5, 200)
    swing_highs_m5, swing_lows_m5 = detect_swings(df_m5)
    bos_m5 = detect_bos(df_m5, swing_highs_m5, swing_lows_m5)

    if direction == "buy" and bos_m5 != "bullish_bos":
        return None

    if direction == "sell" and bos_m5 != "bearish_bos":
        return None


    # ===============================
    # M5 FVG ENTRY FILTER
    # ===============================
    fvg_zones = detect_fvg(df_m5)

    if not fvg_zones:
        return None

    last_fvg = fvg_zones[-1]

    if direction == "buy" and last_fvg["type"] != "bullish":
        return None

    if direction == "sell" and last_fvg["type"] != "bearish":
        return None

    # price must be inside FVG zone
    current_price = df_m5['close'].iloc[-1]

    if not (last_fvg["low"] <= current_price <= last_fvg["high"]):
        return None

    return direction

def run():

    tracker = TradeTracker()

    while True:

        if not check_global_limits(tracker):
            time.sleep(60)
            continue

        for symbol_config in CONFIG["symbols"]:

            if not symbol_config["enabled"]:
                continue

            symbol = symbol_config["name"]

            if not check_symbol_limits(symbol_config, tracker):
                continue

            if has_open_position(symbol):
                continue

            # signal = generate_signal(symbol)
            signal = smc_analysis(symbol)

            if signal is None:
                continue

            print(f"{symbol} Signal: {signal}")

            strategy_cfg = CONFIG["strategy"]
            sl_points = strategy_cfg["stop_loss_points"]
            tp_points = strategy_cfg["take_profit_points"]

            lot = calculate_lot(symbol_config, symbol, sl_points)

            if lot is None:
                continue

            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                continue

            if signal == "buy":
                price = tick.ask
                order_type = mt5.ORDER_TYPE_BUY
            else:
                price = tick.bid
                order_type = mt5.ORDER_TYPE_SELL

            if not check_margin(symbol, lot, price, order_type):
                continue

            result = send_order(symbol, signal, lot, sl_points, tp_points)

            if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Trade executed on {symbol}")
                tracker.record_trade(symbol)
            else:
                print(f"Trade failed on {symbol}")

        time.sleep(15)


# ------------------------------------------------------------
# START SYSTEM
# ------------------------------------------------------------

if __name__ == "__main__":
    connect_mt5()
    run()
