import yfinance as yf
import pandas as pd
import requests

STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN"
CHAT_ID = "PASTE_YOUR_CHAT_ID"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_weekly(symbol):
    df = yf.download(symbol, period="2y", interval="1wk", progress=False)
    df.dropna(inplace=True)
    return df

def bullish_bat(df):
    low = df['Low'].rolling(3).min().iloc[-3]
    high = df['High'].rolling(3).max().iloc[-3]

    fib_58 = high - (high - low) * 0.58
    fib_618 = high - (high - low) * 0.618

    last = df.iloc[-1]

    if fib_618 <= last.Close <= fib_58 and last.Close > last.Open:
        return True, fib_618, fib_58

    return False, None, None

for stock in STOCKS:
    try:
        df = get_weekly(stock)
        found, f618, f58 = bullish_bat(df)
        if found:
            send_alert(
                f"🚨 WEEKLY BULLISH BAT\n"
                f"Stock: {stock}\n"
                f"Entry Zone: {round(f618,2)} – {round(f58,2)}\n\n"
                f\"Macha! 0.58 Fib la reaction ready 🚀\"
            )
    except:
        pass
