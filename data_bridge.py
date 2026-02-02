import yfinance as yf
import firebase_admin
from firebase_admin import credentials, db
import os
import json

def ejecutar_motor_kira():
    print("🚀 Kira iniciando motor de análisis...")
    
    # 1. CARGAR CEREBRO (brain.json)
    try:
        with open('brain.json', 'r') as f:
            cerebro = json.load(f)
        print(f"🧠 Cerebro cargado: Modo {cerebro['configuracion']['riesgo']}")
    except Exception as e:
        print(f"❌ Error al leer brain.json: {e}")
        return

    # 2. CONECTAR A FIREBASE
    # Usamos el secreto de GitHub para las credenciales
    firebase_config = os.environ.get('FIREBASE_CONFIG')
    if not firebase_config:
        print("❌ Error: No se encontró FIREBASE_CONFIG en los secretos de GitHub.")
        return

    try:
        if not firebase_admin._apps:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            # REEMPLAZA ESTA URL con la de tu Realtime Database
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'
            })
    except Exception as e:
        print(f"❌ Error de conexión Firebase: {e}")
        return

    # 3. OBTENER DATOS DE MERCADO (EUR/USD)
    try:
        ticker = yf.Ticker("EURUSD=X")
        data = ticker.history(period="1d", interval="1m")
        precio_actual = data['Close'].iloc[-1]
        print(f"📈 Precio EURUSD: {precio_actual}")
    except Exception as e:
        print(f"❌ Error al obtener precio: {e}")
        return

    # 4. LÓGICA KIRA (Materialización del Cerebro)
    # Aquí simulamos la detección de FVG basada en el bias del brain.json
    fvg_status = "BUSCANDO FVG..."
    bias = cerebro['estrategia']['bias_diario']
    
    if bias == "BULLISH":
        fvg_status = "COMPRA ACTIVA (FVG DETECTADO)"
    else:
        fvg_status = "VENTA ACTIVA (FVG DETECTADO)"

    # 5. ENVIAR A FIREBASE
    ref = db.reference('trading/EURUSD')
    ref.update({
        'precio': str(round(precio_actual, 5)),
        'fvg': fvg_status,
        'tendencia': bias,
        'last_update': str(data.index[-1])
    })
    
    print("✅ Datos enviados con éxito. Kira está en línea.")

if __name__ == "__main__":
    ejecutar_motor_kira()
