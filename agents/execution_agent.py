import MetaTrader5 as mt5
import csv
from datetime import datetime
from config import MAGIC_NUMBER

def place_trade(symbol, signal, lot, sl, tp):

    tick = mt5.symbol_info_tick(symbol)

    if signal == "BUY":
        price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY
    else:
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "AI_SYSTEM",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    log_trade(signal, lot, price)
    print(result)

def log_trade(signal, lot, price):

    with open("logs/trades.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), signal, lot, price])
