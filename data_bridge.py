import yfinance as yf
import requests
import json
from datetime import datetime
import time

def ejecutar_motor_kira():
    print("🚀 INICIANDO PULSO NEURAL...")
    intentos = 0
    max_intentos = 3
    
    while intentos < max_intentos:
        try:
            # 1. Obtener precio real
            ticker = yf.Ticker("EURUSD=X")
            df = ticker.history(period="1d", interval="1m").tail(1)
            
            if df.empty:
                raise Exception("Yahoo Finance no respondió")

            precio_actual = df['Close'].iloc[-1]
            
            # 2. Preparar paquete
            payload = {
                "precio": "{:.5f}".format(precio_actual),
                "last_update": datetime.now().strftime("%H:%M:%S"),
                "fvg": "SISTEMA OPERATIVO ✅",
                "riesgo": "OPTIMIZADO"
            }

            # 3. Enviar a npoint (Tu ID: 50a3a47c4e1b58827a76)
            # Usamos json=payload para que npoint lo acepte correctamente
            response = requests.post(
                "https://api.npoint.io/50a3a47c4e1b58827a76", 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ DATOS ENVIADOS: {precio_actual}")
                break # Salir del bucle si tuvo éxito
            else:
                print(f"⚠️ Error en servidor: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Intento {intentos + 1} fallido: {e}")
            time.sleep(5) # Esperar 5 segundos antes de reintentar
            intentos += 1

if __name__ == "__main__":
    ejecutar_motor_kira()
