import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# CONFIGURACIÓN DEL PUENTE (Usa tu URL de npoint)
BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def run_neural_analysis():
    print("🧠 KIRA NEURAL ENGINE: ANALYZING ALL TIMEFRAMES...")
    try:
        # 1. DATA COLLECTION (M1 para Scalping, M15/H1 para Institucional)
        ticker = yf.Ticker("EURUSD=X")
        df_m1 = ticker.history(period="1d", interval="1m")
        df_m15 = ticker.history(period="5d", interval="15m")
        
        if df_m1.empty or df_m15.empty: 
            print("❌ Error: Datos de mercado no disponibles.")
            return

        # --- LÓGICA INSTITUCIONAL (H1/M15) ---
        df_m15['ATR'] = calculate_atr(df_m15)
        current_atr = df_m15['ATR'].iloc[-1]
        last_price = df_m1['Close'].iloc[-1]
        
        # Detección de Liquidez (Sweeps)
        swing_high = df_m15['High'].iloc[-10:-1].max()
        swing_low = df_m15['Low'].iloc[-10:-1].min()
        
        # --- LÓGICA SCALPING (M1) ---
        delta = df_m1['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_val = 100 - (100 / (1 + rs)).iloc[-1]

        # DETERMINACIÓN DE SEÑAL Y BIAS
        bias = "NEUTRAL"
        signal = "WAITING"
        color = "gray"
        
        # Sniper Entry (Institutional Sweep + Scalp Confirmation)
        if last_price < swing_low and rsi_val < 35:
            bias = "ALCISTA (INSTITUCIONAL)"
            signal = "SCALP BUY (OVERSOLD SWEEP)"
            color = "green"
        elif last_price > swing_high and rsi_val > 65:
            bias = "BAJISTA (INSTITUCIONAL)"
            signal = "SCALP SELL (OVERBOUGHT SWEEP)"
            color = "red"

        # CÁLCULO DE NIVELES (Sniper Precision)
        sl_dist = current_atr * 1.5
        sl = last_price - sl_dist if "BUY" in signal or color == "green" else last_price + sl_dist
        tp1 = last_price + (sl_dist * 2) if "BUY" in signal or color == "green" else last_price - (sl_dist * 2)
        tp2 = last_price + (sl_dist * 4) if "BUY" in signal or color == "green" else last_price - (sl_dist * 4)

        # 2. PAQUETE DE DATOS UNIFICADO
        payload = {
            "p": "{:.5f}".format(last_price),
            "bias": bias,
            "sig": signal,
            "rsi": "{:.2f}".format(rsi_val),
            "volatility": "{:.6f}".format(current_atr),
            "sl": "{:.5f}".format(sl),
            "tp1": "{:.5f}".format(tp1),
            "tp2": "{:.5f}".format(tp2),
            "tp": "{:.5f}".format(tp1), # Para compatibilidad con scalper.html
            "col": color,
            "time": datetime.now().strftime("%H:%M:%S")
        }

        # ENVIAR AL PUENTE
        response = requests.post(BIN_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ SINCRONIZACIÓN EXITOSA | P: {payload['p']} | RSI: {payload['rsi']}")

    except Exception as e:
        print(f"❌ ERROR EN EL MOTOR: {e}")

if __name__ == "__main__":
    run_neural_analysis()
