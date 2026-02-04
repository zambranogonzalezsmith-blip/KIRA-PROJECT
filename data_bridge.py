import yfinance as yf
import requests
from datetime import datetime

BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"

def get_smc_data(symbol, interval, periods):
    df = yf.Ticker(symbol).history(period="5d", interval=interval)
    if len(df) < 3: return "DATA_ERR"
    
    # Lógica FVG simplificada
    last_3 = df.tail(3)
    fvg = "NO"
    if last_3['High'].iloc[0] < last_3['Low'].iloc[2]: fvg = "BULLISH"
    if last_3['Low'].iloc[0] > last_3['High'].iloc[2]: fvg = "BEARISH"
    
    return {"price": df['Close'].iloc[-1], "fvg": fvg}

def ejecutar_escaneo_total():
    print("🧠 KIRA MULTI-TIMEFRAME ANALYSIS STARTING...")
    try:
        # Analizando temporalidades clave
        h4 = get_smc_data("EURUSD=X", "1h", 100) # H4 aproximado con 1h
        h1 = get_smc_data("EURUSD=X", "1h", 50)
        m15 = get_smc_data("EURUSD=X", "15m", 50)

        payload = {
            "p": "{:.5f}".format(m15['price']),
            "h4_fvg": h4['fvg'],
            "h1_fvg": h1['fvg'],
            "m15_fvg": m15['fvg'],
            "time": datetime.now().strftime("%H:%M:%S"),
            "bias": "ALINEADO" if h1['fvg'] == m15['fvg'] else "MIXTO"
        }

        requests.post(BIN_URL, json=payload, timeout=10)
        print(f"✅ SINCRONIZACIÓN COMPLETA: {payload['bias']}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    ejecutar_escaneo_total()
