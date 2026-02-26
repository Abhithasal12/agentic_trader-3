
import MetaTrader5 as mt5
account = 5044152817
password = "C*2vAdZq"
server = "MetaQuotes-Demo"

mt5.initialize(login=account, password=password, server=server)

def connect():
    if not mt5.initialize():
        print("MT5 initialization failed")
        quit()
    print("Connected to MT5")
