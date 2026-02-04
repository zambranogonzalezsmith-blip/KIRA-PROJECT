import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime

BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def run_neural_analysis():
    print(f"🧠 KIRA GLOBAL ENGINE START [{datetime.now().strftime('%H:%M:%S')}]")
    try:
        # 1. DATA COLLECTION
        eurusd = yf.Ticker("EURUSD=X").history(period="1d", interval="1m")
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m") # Índice Dólar
        
        if eurusd.empty or dxy.empty: return

        # Cálculo EURUSD
        last_p = eurusd['Close'].iloc[-1]
        delta = eurusd['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]

        # ANÁLISIS DXY (FILTRO DE SEGURIDAD)
        dxy_p = dxy['Close'].iloc[-1]
        dxy_prev = dxy['Close'].iloc[-2]
        dxy_trend = "BULLISH" if dxy_p > dxy_prev else "BEARISH"
        
        # 2. ESCANEO MULTI-ACTIVO
        gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        oil = yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1]
        btc = yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1]

        # DETERMINACIÓN DE SEÑAL CON FILTRO DXY
        bias, signal, color = "NEUTRAL", "BUSCANDO", "gray"
        
        # Si el DXY está subiendo fuerte, no compramos EURUSD (evitamos trampas)
        if last_p < eurusd['Low'].iloc[-15:-1].min() and rsi < 32:
            if dxy_trend == "BEARISH": # Dólar débil = Compra segura
                bias, signal, color = "ALCISTA (SMC)", "BUY CONFIRMED", "green"
            else:
                bias, signal, color = "PRECAUCIÓN", "DXY STRONG (WAIT)", "orange"
        
        elif last_p > eurusd['High'].iloc[-15:-1].max() and rsi > 68:
            if dxy_trend == "BULLISH": # Dólar fuerte = Venta segura
                bias, signal, color = "BAJISTA (SMC)", "SELL CONFIRMED", "red"
            else:
                bias, signal, color = "PRECAUCIÓN", "DXY WEAK (WAIT)", "orange"

        # NIVELES
        sl_d = calculate_atr(yf.Ticker("EURUSD=X").history(period="5d", interval="15m")).iloc[-1] * 1.8
        sl = last_p - sl_d if color == "green" else last_p + sl_d
        tp = last_p + (sl_d * 2.5) if color == "green" else last_p - (sl_d * 2.5)

        payload = {
            "p": "{:.5f}".format(last_p),
            "bias": bias,
            "sig": signal,
            "rsi": "{:.2f}".format(rsi),
            "volatility": "{:.6f}".format(sl_d/1.8),
            "sl": "{:.5f}".format(sl),
            "tp1": "{:.5f}".format(tp),
            "col": color,
            "gold": "{:.2f}".format(gold),
            "oil": "{:.2f}".format(oil),
            "btc": "{:.0f}".format(btc),
            "dxy": "{:.2f}".format(dxy_p),
            "dxy_t": dxy_trend,
            "time": datetime.now().strftime("%H:%M:%S")
        }

        requests.post(BIN_URL, json=payload, timeout=10)
        print(f"✅ GLOBAL SYNC OK | DXY: {payload['dxy']} ({dxy_trend})")

    except Exception as e: print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_neural_analysis()
