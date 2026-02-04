import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# CONFIGURACIÓN DEL PUENTE
BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def institutional_scan():
    print("🏦 KIRA INSTITUTIONAL ALGO: INITIATING...")
    try:
        # 1. Obtener Data Institucional (H1 para estructura, M15 para entrada)
        ticker = yf.Ticker("EURUSD=X")
        df = ticker.history(period="5d", interval="15m")
        
        if len(df) < 50: return

        # 2. Calcular Volatilidad Bancaria (ATR)
        df['ATR'] = calculate_atr(df)
        current_atr = df['ATR'].iloc[-1]
        last_price = df['Close'].iloc[-1]
        
        # 3. Detectar Estructura (Swing Highs/Lows)
        last_high = df['High'].iloc[-5:-1].max()
        last_low = df['Low'].iloc[-5:-1].min()
        
        # 4. Lógica de Entrada Sniper (SMC)
        # Buscamos manipulación: Precio rompe un bajo pero cierra arriba (Sweep)
        signal = "NEUTRAL (ESPERANDO LIQUIDEZ)"
        bias = "RANGO"
        sl_pips = 0.0
        entry_price = 0.0
        
        # Algoritmo de Compra (Bullish Sniper)
        if df['Low'].iloc[-1] < last_low and df['Close'].iloc[-1] > last_low:
            signal = "BUY LIMIT (LIQUIDITY SWEEP)"
            bias = "ALCISTA (INSTITUCIONAL)"
            entry_price = last_price
            # SL Matemático: Bajo de la vela + 1.5 veces el ATR (Para evitar stop hunt)
            sl_price = df['Low'].iloc[-1] - (current_atr * 1.5)
            tp1 = entry_price + (entry_price - sl_price) * 2  # Ratio 1:2
            tp2 = entry_price + (entry_price - sl_price) * 3.5 # Ratio 1:3.5
            tp3 = entry_price + (entry_price - sl_price) * 5  # Ratio 1:5 (Runner)

        # Algoritmo de Venta (Bearish Sniper)
        elif df['High'].iloc[-1] > last_high and df['Close'].iloc[-1] < last_high:
            signal = "SELL LIMIT (LIQUIDITY SWEEP)"
            bias = "BAJISTA (INSTITUCIONAL)"
            entry_price = last_price
            # SL Matemático: Alto de la vela + 1.5 veces el ATR
            sl_price = df['High'].iloc[-1] + (current_atr * 1.5)
            tp1 = entry_price - (sl_price - entry_price) * 2
            tp2 = entry_price - (sl_price - entry_price) * 3.5
            tp3 = entry_price - (sl_price - entry_price) * 5

        else:
            # Si no hay señal, calculamos niveles teóricos
            sl_price = last_price - (current_atr * 2) # Referencial
            tp1, tp2, tp3 = 0.0, 0.0, 0.0

        # 5. Formatear Paquete JSON Bancario
        payload = {
            "price": "{:.5f}".format(last_price),
            "bias": bias,
            "signal": signal,
            "volatility": "{:.5f}".format(current_atr),
            "trade_setup": {
                "entry": "{:.5f}".format(entry_price) if entry_price else "---",
                "sl": "{:.5f}".format(sl_price),
                "tp1": "{:.5f}".format(tp1) if tp1 else "---",
                "tp2": "{:.5f}".format(tp2) if tp2 else "---",
                "tp3": "{:.5f}".format(tp3) if tp3 else "---"
            },
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        requests.post(BIN_URL, json=payload, timeout=10)
        print(f"✅ ALGO EXECUTION COMPLETED: {bias}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    institutional_scan()
