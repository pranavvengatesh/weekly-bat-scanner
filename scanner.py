import yfinance as yf
import pandas as pd
import requests
import os
import time

# 🔹 STOCK LIST (ADD AS MANY AS YOU WANT)
STOCKS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "SBIN.NS","LT.NS","AXISBANK.NS","KOTAKBANK.NS","ITC.NS",
    "HINDUNILVR.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS",
    "SUNPHARMA.NS","HCLTECH.NS","WIPRO.NS","ADANIPORTS.NS"
]

# 🔐 Secrets from ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def get_weekly(symbol):
    df = yf.download(symbol, period="2y", interval="1wk", progress=False)
    return df.dropna()

def bullish_bat(df):
    if len(df) < 10:
        return False, None, None

    low = df['Low'].rolling(3).min().iloc[-3]
    high = df['High'].rolling(3).max().iloc[-3]

    if low >= high:
        return False, None, None

    fib58 = high - (high - low) * 0.58
    fib618 = high - (high - low) * 0.618

    last = df.iloc[-1]

    if fib618 <= last.Close <= fib58 and last.Close > last.Open:
        return True, round(fib618, 2), round(fib58, 2)

    return False, None, None

# 🔔 START SCAN
found_any = False

for stock in STOCKS:
    try:
        df = get_weekly(stock)
        hit, f618, f58 = bullish_bat(df)

        if hit:
            found_any = True
            send_alert(
                f"🚨 WEEKLY BULLISH BAT\n"
                f"Stock: {stock}\n"
                f"Entry Zone: {f618} – {f58}\n\n"
                f"Macha! 0.58 Fib la reaction ready 🚀"
            )

        time.sleep(1)  # avoid API throttling

    except Exception as e:
        print(f"Error in {stock}: {e}")

if not found_any:
    send_alert("ℹ️ Weekly scan done. No Bullish Bat found this week.")




send_alert("✅ Weekly scanner deployed successfully")

