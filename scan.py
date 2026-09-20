import os
import requests
import yfinance as yf
import pandas as pd

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def telegram(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mesaj
        },
        timeout=20
    )


# Gümüş
data = yf.download(
    "SI=F",
    period="2d",
    interval="5m",
    progress=False,
    auto_adjust=False
)

if data.empty:
    telegram("⚠️ EMRE GÜMÜŞ RADAR\n\nGümüş verisi alınamadı.")
    raise SystemExit

close = data["Close"].squeeze().dropna()

# EMA
ema9 = close.ewm(span=9, adjust=False).mean()
ema21 = close.ewm(span=21, adjust=False).mean()

# RSI
delta = close.diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))

fiyat = float(close.iloc[-1])
rsi_son = float(rsi.iloc[-1])
ema9_son = float(ema9.iloc[-1])
ema21_son = float(ema21.iloc[-1])

risk = 0

if rsi_son < 45:
    risk += 1

if ema9_son < ema21_son:
    risk += 1

if fiyat < ema21_son:
    risk += 1

if rsi_son < 35:
    risk += 1

risk_text = {
    0: "🟢 NORMAL",
    1: "🟡 DİKKAT",
    2: "🟠 RİSK ARTIYOR",
    3: "🔴 GÜÇLÜ UYARI",
    4: "🚨 ÇOK GÜÇLÜ UYARI"
}[risk]

mesaj = f"""📡 EMRE GÜMÜŞ RADAR

🥈 Gümüş: {fiyat:.2f}
📊 RSI: {rsi_son:.1f}
📈 EMA9: {ema9_son:.2f}
📉 EMA21: {ema21_son:.2f}

⚠️ Risk: {risk}/4
{risk_text}

Bu sistem otomatik işlem yapmaz.
Sadece erken uyarı üretir.
"""

telegram(mesaj)
