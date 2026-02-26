CONFIG = {

    # ============================================================
    # SYMBOL SETTINGS
    # ============================================================
    "symbols": [
        {
            "name": "XAUUSD",
            "enabled": True,
            "risk_percent": 1.0,
            "max_trades_per_day": 10,

            # Lot sizing controls
            "lot_settings": {
                "use_fixed_lot": False,
                "fixed_lot": 0.01,
                "min_lot": 0.02,
                "max_lot": 0.10
            }
        },
        {
            "name": "EURUSD",
            "enabled": True,
            "risk_percent": 1.0,
            "max_trades_per_day": 10,

            "lot_settings": {
                "use_fixed_lot": False,
                "fixed_lot": 0.10, #0.10
                "min_lot": 0.05,#0.05
                "max_lot": 0.50
            }
        },
        {
            "name": "USDJPY",
            "enabled": True,
            "risk_percent": 1.0,
            "max_trades_per_day": 10,

            # Lot sizing controls
            "lot_settings": {
                "use_fixed_lot": False,
                "fixed_lot": 0.03,
                "min_lot": 0.02,
                "max_lot": 0.10
            }
        },
    ],

    # ============================================================
    # GLOBAL RISK CONTROL
    # ============================================================
    "global_risk": {
        "max_daily_loss": 100,
        "max_total_trades": 6,
    },

    # ============================================================
    # STRATEGY SETTINGS
    # ============================================================
    "strategy": {
        "timeframe": "M5",
        "fast_ema": 9,
        "slow_ema": 21,
        "rsi_period": 14,
        "rsi_buy_level": 55,
        "rsi_sell_level": 45,
        "stop_loss_points": 200,   # Fixed SL distance
        "take_profit_points": 1000  # RR 1:2
    },

    # ============================================================
    # MT5 SETTINGS
    # ============================================================
    "mt5": {
        "magic_number": 900001,
        "deviation": 20,
    }
}
