import yfinance as yf
import pandas as pd
import time
import json
import firebase_admin
from firebase_admin import credentials, db

# --- CONFIGURACIÓN DE SEGURIDAD ---
# 1. Coloca aquí el nombre del archivo JSON que descargaste de Firebase
# 2. Asegúrate de que ese archivo esté en la misma carpeta /finance
try:
    cred = credentials.Certificate("tu-archivo-firebase.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tu-proyecto-kira.firebaseio.com/' # Reemplaza con tu URL de Firebase
    })
    print("✅ Conexión con la Nube de Kira establecida.")
except Exception as e:
    print(f"❌ Error al conectar con Firebase: {e}")

# Activos a monitorear
ACTIVOS = ["EURUSD=X", "GC=F"] # EUR/USD y ORO

def analizar_smc(df):
    """Lógica de Kira para detectar zonas de Smart Money"""
    last_close = df['Close'].iloc[-1]
    # Detección simple de FVG (Fair Value Gap)
    fvg = "NEUTRAL"
    if df['Low'].iloc[-3] > df['High'].iloc[-1]:
        fvg = "BEARISH FVG (VENTA)"
    elif df['High'].iloc[-3] < df['Low'].iloc[-1]:
        fvg = "BULLISH FVG (COMPRA)"
    
    return {
        "precio": round(last_close, 5),
        "fvg": fvg,
        "tendencia": "ALCISTA" if last_close > df['Close'].iloc[-20] else "BAJISTA"
    }

def enviar_a_nube(simbolo, analisis):
    """Envía los datos al index.html a través de Firebase"""
    try:
        # Limpiamos el nombre del símbolo para Firebase
        id_limpio = simbolo.replace("=X", "").replace("=F", "")
        ref = db.reference(f'trading/{id_limpio}')
        ref.set({
            'precio': analisis['precio'],
            'fvg': analisis['fvg'],
            'tendencia': analisis['tendencia'],
            'timestamp': time.strftime("%H:%M:%S")
        })
        print(f"📡 [Kira] Datos de {id_limpio} actualizados en la plataforma online.")
    except Exception as e:
        print(f"❌ Error al enviar datos: {e}")

def ejecutar_puente():
    print("=== KIRA DATA BRIDGE: OPERATIVO ===")
    while True:
        try:
            for activo in ACTIVOS:
                # Descarga de datos reales de Forex/Oro
                data = yf.download(activo, period="1d", interval="15m", progress=False)
                if not data.empty:
                    analisis = analizar_smc(data)
                    enviar_a_nube(activo, analisis)
            
            # Esperar 60 segundos para la siguiente actualización
            time.sleep(60)
            
        except Exception as e:
            print(f"⚠️ Error en el ciclo de Kira: {e}")
            time.sleep(10)

if __name__ == "__main__":
    ejecutar_puente()
