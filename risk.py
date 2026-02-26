import MetaTrader5 as mt5


def calculate_lot(symbol_config, symbol, stop_loss_points):
    """
    Calculates lot size using either:
    - Fixed lot mode
    - Risk % based dynamic lot
    """

    lot_settings = symbol_config["lot_settings"]

    # 1️⃣ Fixed lot mode
    if lot_settings["use_fixed_lot"]:
        lot = lot_settings["fixed_lot"]
        return round(lot, 2)

    # 2️⃣ Dynamic risk-based lot
    account = mt5.account_info()
    if account is None:
        print("Failed to get account info")
        return None

    balance = account.balance
    risk_percent = symbol_config["risk_percent"]
    risk_amount = balance * (risk_percent / 100)

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol info not found: {symbol}")
        return None

    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size

    if tick_value == 0 or tick_size == 0:
        print("Invalid tick values")
        return None

    # Risk per lot
    value_per_point = tick_value / tick_size
    lot = risk_amount / (stop_loss_points * value_per_point)

    # Clamp between min and max lot
    lot = max(lot_settings["min_lot"], lot)
    lot = min(lot_settings["max_lot"], lot)

    return round(lot, 2)


def check_margin(symbol, lot, price, order_type):
    """
    Checks if account has enough free margin
    """

    margin = mt5.order_calc_margin(order_type, symbol, lot, price)

    if margin is None:
        print("Margin calculation failed")
        return False

    account = mt5.account_info()
    if account is None:
        print("Failed to get account info")
        return False

    if account.margin_free < margin:
        print("Not enough free margin")
        return False

    return True
