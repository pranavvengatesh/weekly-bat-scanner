import yfinance as yf
import pandas as pd
import requests
import os
import time
import random

# ===============================
# 🔹 STOCK LIST
# ===============================
STOCKS = [
    "KSOLVES.NS","STELLANT.NS","SHANTIDOOT.NS","ICODEX.NS","WAAREERTL.NS",
    "SHILCHART.NS","SIGMASOLVE.NS","ONEGLOBAL.NS","SHAKTIPUMP.NS","ARROWGREEN.NS",
    "ALPEXSOLAR.NS","JYOTIRESIN.NS","COALINDIA.NS","TAPARIA.NS","VIRTUALG.NS",
    "GANESHHOUC.NS","KRONOX.NS","ORIANAPOWER.NS","EVANSELECT.NS","ACE.NS",
    "ASHOKA.NS","RMCSWITCH.NS","SESHAA.NS","GLOBALVECT.NS","BBTC.NS",

    "TRANSRAILL.NS","PATELCHEM.NS","WAAREEENER.NS","IWARE.NS","SHARDAMOTR.NS",
    "CIGNITITEC.NS","BLS.NS","KAYTEX.NS","ESCORP.NS","TAALENT.NS",
    "RAJOOENG.NS","GYANDEV.NS","SIDDHIKA.NS","SRMCON.NS","AUTHUM.NS",

    "CHAMUNDA.NS","MAHALAXMI.NS","KOTHARIPET.NS","SAMAY.NS","ALLETECH.NS",
    "NMDC.NS","KALYANICAS.NS","KARBONSTEEL.NS","NAGREEKCAP.NS","SYSTANGO.NS",

    "VINSYS.NS","HINDHARDY.NS","DHANUKA.NS","URBANENV.NS","DANLAW.NS",
    "LIKHITHA.NS","AMWILL.NS","GANDHISPL.NS","SUPREMEPWR.NS","INTLCONV.NS",
    "PIXTRANS.NS","CAPNUM.NS","BEPL.NS","PREVEST.NS","MAGNAELQ.NS",

    "EPIGRAL.NS","NITTAGEL.NS","AGARWAL.NS","AHIMSAMIN.NS","SAKSOFT.NS",
    "ACCENTMIC.NS","ALUFLUOR.NS","AMEYAPREC.NS","PDMJEPAPER.NS","GUJINTRX.NS",

    "SHRITECHTEX.NS","JUPITER.NS","PDPSHIP.NS","EXPLEOSOL.NS","INDOUS.NS",
    "DBCORP.NS","SNLB.NS","SELLO.NS","SILICONR.NS","DHABRIYA.NS",
    "MARCO.NS","ASALCBR.NS","SHREEOSFM.NS","KAKAIND.NS","TALBROAUTO.NS",

    "ATCENERGY.NS","SHREEGANESH.NS","CREDO.NS","CROWNLIFT.NS","GEOJITFSL.NS",
    "RUCHIRA.NS","CONTROLPR.NS","KWALITY.NS","SWARAJSUIT.NS","GOELFOOD.NS",

    "REFRACTORY.NS","KONTOR.NS","SHRIBALAJI.NS"
]

# ===============================
# 🔐 ENV VARIABLES
# ===============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===============================
# 🔔 TELEGRAM ALERT
# ===============================
def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ===============================
# 📊 BATCH FETCH (RATE LIMIT SAFE)
# ===============================
def fetch_batch(symbols):
    try:
        df = yf.download(
            symbols,
            period="2y",
            interval="1wk",
            group_by="ticker",
            progress=False
        )
        return df
    except Exception as e:
        print("❌ Batch fetch error:", e)
        return None

# ===============================
# 🦇 BULLISH BAT LOGIC (SAFE)
# ===============================
def bullish_bat(df):
    if df is None or df.empty or len(df) < 10:
        return False, None, None

    # Force scalar values
    low = df['Low'].rolling(3).min().iloc[-3].item()
    high = df['High'].rolling(3).max().iloc[-3].item()

    if low >= high:
        return False, None, None

    fib_58 = high - (high - low) * 0.58
    fib_618 = high - (high - low) * 0.618

    last_close = df['Close'].iloc[-1].item()
    last_open = df['Open'].iloc[-1].item()

    if fib_618 <= last_close <= fib_58 and last_close > last_open:
        return True, round(fib_618, 2), round(fib_58, 2)

    return False, None, None

# ===============================
# 🔁 SCAN EXECUTION
# ===============================
BATCH_SIZE = 2        # Safe for Yahoo
SLEEP_TIME = 12

found_any = False

for i in range(0, len(STOCKS), BATCH_SIZE):
    batch = STOCKS[i:i + BATCH_SIZE]
    print(f"\n🔄 Fetching batch: {batch}")

    batch_df = fetch_batch(batch)
    if batch_df is None:
        time.sleep(SLEEP_TIME)
        continue

    for stock in batch:
        try:
            if stock not in batch_df:
                print(f"❌ {stock}: No data returned")
                continue

            df = batch_df[stock].dropna()
            print(f"✅ {stock}: {len(df)} weekly candles fetched")

            found, f618, f58 = bullish_bat(df)

            if found:
                found_any = True
                send_alert(
                    f"🚨 WEEKLY BULLISH BAT\n"
                    f"Stock: {stock}\n"
                    f"Entry Zone: {f618} – {f58}\n\n"
                    f"Macha! 0.58 Fib la reaction ready 🚀"
                )

        except Exception as e:
            print(f"❌ Error in {stock}: {e}")

    sleep_time = SLEEP_TIME + random.randint(2, 5)
    print(f"⏳ Sleeping {sleep_time}s to avoid Yahoo rate limit...")
    time.sleep(sleep_time)

# ===============================
# ℹ️ FINAL MESSAGE
# ===============================
if not found_any:
    send_alert("ℹ️ Weekly scan done. No Bullish Bat found this week.")
