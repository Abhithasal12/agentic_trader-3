import MetaTrader5 as mt5
from datetime import datetime
from config import CONFIG


# ------------------------------------------------------------
# DAILY TRACKER
# ------------------------------------------------------------

class TradeTracker:

    def __init__(self):
        self.daily_trades = {}
        self.daily_loss = 0
        self.total_trades = 0
        self.current_day = datetime.now().date()

    def reset_if_new_day(self):
        today = datetime.now().date()
        if today != self.current_day:
            self.daily_trades = {}
            self.daily_loss = 0
            self.total_trades = 0
            self.current_day = today

    def record_trade(self, symbol):
        self.daily_trades[symbol] = self.daily_trades.get(symbol, 0) + 1
        self.total_trades += 1

    def record_loss(self, loss_amount):
        if loss_amount < 0:
            self.daily_loss += abs(loss_amount)

    def symbol_trade_count(self, symbol):
        return self.daily_trades.get(symbol, 0)


# ------------------------------------------------------------
# CHECK OPEN POSITION
# ------------------------------------------------------------

def has_open_position(symbol):
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0


# ------------------------------------------------------------
# GLOBAL LIMIT CHECK
# ------------------------------------------------------------

def check_global_limits(tracker):

    tracker.reset_if_new_day()

    if tracker.total_trades >= CONFIG["global_risk"]["max_total_trades"]:
        print("Max total trades reached")
        return False

    if tracker.daily_loss >= CONFIG["global_risk"]["max_daily_loss"]:
        print("Max daily loss reached")
        return False

    return True


# ------------------------------------------------------------
# SYMBOL LIMIT CHECK
# ------------------------------------------------------------

def check_symbol_limits(symbol_config, tracker):

    symbol = symbol_config["name"]
    max_trades = symbol_config["max_trades_per_day"]

    if tracker.symbol_trade_count(symbol) >= max_trades:
        print(f"Max trades reached for {symbol}")
        return False

    return True


# ------------------------------------------------------------
# SEND ORDER
# ------------------------------------------------------------

def send_order(symbol, signal, lot, sl_points, tp_points):

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print("Symbol not found")
        return None

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("Tick not found")
        return None

    point = symbol_info.point

    if signal == "buy":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl = price - sl_points * point
        tp = price + tp_points * point
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = price + sl_points * point
        tp = price - tp_points * point

    # Try all possible filling modes
    filling_modes = [
        mt5.ORDER_FILLING_RETURN,
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_FOK
    ]

    for mode in filling_modes:

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 900001,
            "comment": "STABLE_ENGINE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mode,
        }

        result = mt5.order_send(request)

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print("Trade placed successfully")
            print(result)
            return result

        else:
            print(f"Filling mode {mode} failed")

    print("All filling modes failed.")
    return None
