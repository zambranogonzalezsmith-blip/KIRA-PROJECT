import yfinance as yf
import requests
import json
from datetime import datetime

def calcular_fvg(df):
    """Detecta ineficiencias en el precio (Fair Value Gap)."""
    if len(df) < 3: return None, 0, 0
    v1_high, v1_low = df['High'].iloc[-3], df['Low'].iloc[-3]
    v3_high, v3_low = df['High'].iloc[-1], df['Low'].iloc[-1]
    
    if v3_low > v1_high: return "COMPRA: FVG DETECTADO", v1_high, v3_low
    if v3_high < v1_low: return "VENTA: FVG DETECTADO", v3_high, v1_low
    return "ESCANEANDO MERCADO...", 0, 0

def ejecutar_motor_kira():
    try:
        # 1. Tu nuevo puente de datos (NPOINT)
        BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"
        
        # 2. Obtener datos reales de EUR/USD
        # Usamos el activo del primer lugar en tus parámetros o EURUSD por defecto
        ticker = yf.Ticker("EURUSD=X")
        df = ticker.history(period="1d", interval="1m").tail(5)
        
        if df.empty:
            print("❌ No se recibieron datos de Yahoo Finance.")
            return

        precio_actual = df['Close'].iloc[-1]
        fvg_msg, top, bottom = calcular_fvg(df)

        # 3. Crear el paquete de datos (JSON)
        payload = {
            "precio": str(round(precio_actual, 5)),
            "fvg": fvg_msg,
            "fvg_top": float(top),
            "fvg_bottom": float(bottom),
            "riesgo": "DINÁMICO",
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

        # 4. Enviar datos al puente (Método POST)
        response = requests.post(BIN_URL, json=payload)
        
        if response.status_code == 200:
            print(f"✅ KIRA SINCRONIZADA: {precio_actual} | {fvg_msg}")
        else:
            print(f"⚠️ Error en npoint: {response.status_code}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
