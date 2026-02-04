import yfinance as yf
import requests
import json
from datetime import datetime

def ejecutar_motor_kira():
    try:
        # 1. Configuración del Puente (Tu nuevo ID)
        BIN_URL = "https://api.npoint.io/50a3a47c4e1b58827a76"
        
        # 2. Obtener datos del mercado
        ticker = yf.Ticker("EURUSD=X")
        df = ticker.history(period="1d", interval="1m").tail(1)
        
        if df.empty:
            print("❌ No hay datos de mercado")
            return

        precio_actual = df['Close'].iloc[-1]

        # 3. Crear el paquete de datos
        payload = {
            "precio": str(round(precio_actual, 5)),
            "fvg": "SISTEMA ACTIVO ✅",
            "riesgo": "BAJO",
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "status": "online"
        }

        # 4. Enviar a npoint (esto actualiza tu link automáticamente)
        response = requests.post(BIN_URL, json=payload)
        
        if response.status_code == 200:
            print(f"🚀 KIRA ACTUALIZADA: {precio_actual}")
        else:
            print(f"⚠️ Error de conexión: {response.status_code}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
