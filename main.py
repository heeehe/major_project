from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import numpy as np
import datetime
import time

# Initialize Kite API
API_KEY = "your_api_key"
ACCESS_TOKEN = "your_access_token"
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# Instrument details (e.g., NIFTY 50)
INSTRUMENT_TOKEN = 256265  
TRADING_SYMBOL = "NSE:NIFTY50"
QUANTITY = 1  # Adjust based on your margin

# Track active positions and SL/TP
active_positions = {}

# Calculate Heikin-Ashi candles
def calculate_heikin_ashi(df):
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_close.iloc[i-1]) / 2)
    df['HA_Close'] = ha_close
    df['HA_Open'] = ha_open
    df['HA_High'] = df[['high', 'HA_Open', 'HA_Close']].max(axis=1)
    df['HA_Low'] = df[['low', 'HA_Open', 'HA_Close']].min(axis=1)
    return df

# Calculate MACD
def calculate_macd(df):
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

# Calculate ATR (14-period)
def calculate_atr(df):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift(1))
    low_close = abs(df['low'] - df['close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    return df

# Check entry signals
def check_entry_signal(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Long signal conditions
    long_conditions = (
        latest['HA_Open'] == latest['HA_Low'] and  # Heikin-Ashi open = low
        latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal'] and  # MACD crossover
        (abs(latest['close'] - latest['fib_618']) <= latest['close'] * 0.005 and  # Near Fib 61.8%
        (latest['ATR'] / latest['close']) * 100 > 1.5 and  # ATR > 1.5%
        latest['volume'] > 1.5 * df['volume'].rolling(20).mean().iloc[-1]  # Volume > 1.5x avg
    )
    
    # Short signal conditions (reverse logic)
    short_conditions = (
        latest['HA_Open'] == latest['HA_High'] and
        latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal'] and
        (abs(latest['close'] - latest['fib_618']) <= latest['close'] * 0.005 and
        (latest['ATR'] / latest['close']) * 100 > 1.5 and
        latest['volume'] > 1.5 * df['volume'].rolling(20).mean().iloc[-1]
    )
    
    return "LONG" if long_conditions else "SHORT" if short_conditions else None

# Execute order
def place_order(signal):
    try:
        if signal == "LONG":
            order_id = kite.place_order(
                tradingsymbol=TRADING_SYMBOL,
                exchange=kite.EXCHANGE_NSE,
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=QUANTITY,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS
            )
            print("Long order placed:", order_id)
            active_positions[order_id] = {
                'type': 'LONG',
                'entry_price': df['close'].iloc[-1],
                'trailing_sl': df['close'].iloc[-1] - 0.5 * df['ATR'].iloc[-1]
            }
        elif signal == "SHORT":
            order_id = kite.place_order(
                tradingsymbol=TRADING_SYMBOL,
                exchange=kite.EXCHANGE_NSE,
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=QUANTITY,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS
            )
            print("Short order placed:", order_id)
            active_positions[order_id] = {
                'type': 'SHORT',
                'entry_price': df['close'].iloc[-1],
                'trailing_sl': df['close'].iloc[-1] + 0.5 * df['ATR'].iloc[-1]
            }
    except Exception as e:
        print("Order placement failed:", e)

# Check exit conditions (simplified)
def check_exit_conditions():
    for order_id, position in list(active_positions.items()):
        latest_price = kite.ltp(INSTRUMENT_TOKEN)[str(INSTRUMENT_TOKEN)]['last_price']
        if position['type'] == 'LONG':
            if latest_price >= position['entry_price'] + 1.5 * position['ATR'] or \
               latest_price <= position['trailing_sl']:
                # Exit logic for profit/SL
                pass  # Implement exit order here
        elif position['type'] == 'SHORT':
            if latest_price <= position['entry_price'] - 1.5 * position['ATR'] or \
               latest_price >= position['trailing_sl']:
                # Exit logic
                pass

# Main loop
while True:
    try:
        # Fetch historical data (adjust time frame as needed)
        data = kite.historical_data(INSTRUMENT_TOKEN, 
                                   datetime.datetime.now() - datetime.timedelta(days=5),
                                   datetime.datetime.now(), 
                                   interval='5minute')
        df = pd.DataFrame(data)
        
        # Calculate indicators
        df = calculate_heikin_ashi(df)
        df = calculate_macd(df)
        df = calculate_atr(df)
        
        # Check signals
        signal = check_entry_signal(df)
        if signal:
            place_order(signal)
        
        # Check exits
        check_exit_conditions()
        
        time.sleep(300)  # Wait 5 minutes before next check
    except Exception as e:
        print("Error:", e)
        time.sleep(60)
