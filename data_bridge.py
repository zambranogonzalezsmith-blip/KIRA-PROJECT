import yfinance as yf
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime

def calcular_fvg(df):
    """
    Analiza las últimas 3 velas para detectar un Fair Value Gap real.
    """
    if len(df) < 3:
        return None, 0, 0

    # Velas (v1 es la más antigua, v3 la más reciente)
    v1_high = df['High'].iloc[-3]
    v1_low = df['Low'].iloc[-3]
    v3_high = df['High'].iloc[-1]
    v3_low = df['Low'].iloc[-1]

    # BULLISH FVG: El Low de la vela 3 es mayor al High de la vela 1
    if v3_low > v1_high:
        return "BULLISH", v1_high, v3_low
    
    # BEARISH FVG: El High de la vela 3 es menor al Low de la vela 1
    if v3_high < v1_low:
        return "BEARISH", v3_high, v1_low

    return None, 0, 0

def ejecutar_motor_kira():
    try:
        with open('brain.json', 'r') as f:
            brain = json.load(f)
        with open('trading_params.json', 'r') as f:
            params = json.load(f)
        
        firebase_config = os.environ.get('FIREBASE_CONFIG')
        if not firebase_admin._apps:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'})

        # 1. Obtener datos (pedimos 5 para asegurar el cálculo)
        ticker = yf.Ticker(params['monitoreo']['activos'][0])
        df = ticker.history(period="1d", interval="1m").tail(5)
        
        if df.empty: return

        precio_actual = df['Close'].iloc[-1]
        
        # 2. Calcular FVG Real
        tipo_fvg, fvg_top, fvg_bottom = calcular_fvg(df)

        # 3. Definir estado para la web
        if tipo_fvg == "BULLISH":
            fvg_msg = "COMPRA: FVG DETECTADO"
            bias = "BULLISH"
        elif tipo_fvg == "BEARISH":
            fvg_msg = "VENTA: FVG DETECTADO"
            bias = "BEARISH"
        else:
            fvg_msg = "BUSCANDO LIQUIDEZ..."
            bias = brain['estrategia']['bias_diario']

        # 4. Enviar a Firebase con coordenadas exactas
        ref = db.reference('trading/EURUSD')
        ref.update({
            'precio': str(round(precio_actual, 5)),
            'fvg': fvg_msg,
            'fvg_top': fvg_top,       # <--- Coordenada superior real
            'fvg_bottom': fvg_bottom, # <--- Coordenada inferior real
            'tendencia': bias,
            'riesgo': brain['configuracion']['riesgo'],
            'metodo': brain['estrategia']['metodo'],
            'last_update': datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"✅ Kira analizó el mercado: {fvg_msg} ({fvg_top} - {fvg_bottom})")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
