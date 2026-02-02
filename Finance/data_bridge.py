import yfinance as yf
import pandas as pd
import time
import json

# Configuración de Activos
ACTIVOS = ["EURUSD=X", "GC=F"] # Forex y Oro

def analizar_smc(df):
    """
    Kira detecta zonas de alta probabilidad (SMC)
    """
    last_close = df['Close'].iloc[-1]
    last_low = df['Low'].iloc[-1]
    last_high = df['High'].iloc[-1]
    
    # Lógica de detección de FVG simple para el puente
    fvg = "No detectado"
    if df['Low'].iloc[-3] > df['High'].iloc[-1]:
        fvg = "BAJISTA (Bearish)"
    elif df['High'].iloc[-3] < df['Low'].iloc[-1]:
        fvg = "ALCISTA (Bullish)"
    
    return {
        "precio": round(last_close, 5),
        "fvg": fvg,
        "tendencia": "ALCISTA" if last_close > df['Close'].iloc[-20] else "BAJISTA"
    }

def ejecutar_puente():
    print("=== KIRA DATA BRIDGE: ACTIVADO ===")
    while True:
        try:
            for activo in ACTIVOS:
                # Descargamos datos recientes
                data = yf.download(activo, period="1d", interval="15m", progress=False)
                if not data.empty:
                    analisis = analizar_smc(data)
                    print(f"[{activo}] Precio: {analisis['precio']} | FVG: {analisis['fvg']}")
                    
                    # Aquí Kira prepara los datos para el index.html
                    # En una fase avanzada, esto se sube vía API o WebSocket
            
            # Pausa de 1 minuto para no saturar el sistema
            time.sleep(60)
            
        except Exception as e:
            print(f"Error en el puente de Kira: {e}")
            time.sleep(10)

if __name__ == "__main__":
    ejecutar_puente()
