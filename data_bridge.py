import yfinance as yf
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime

def calcular_fvg(df):
    """Analiza las últimas 3 velas para detectar un Fair Value Gap."""
    if len(df) < 3: return None, 0, 0
    v1_high, v1_low = df['High'].iloc[-3], df['Low'].iloc[-3]
    v3_high, v3_low = df['High'].iloc[-1], df['Low'].iloc[-1]
    
    if v3_low > v1_high: return "BULLISH", v1_high, v3_low
    if v3_high < v1_low: return "BEARISH", v3_high, v1_low
    return None, 0, 0

def ejecutar_motor_kira():
    try:
        # 1. Cargar configuraciones de archivos locales
        with open('brain.json', 'r') as f:
            brain = json.load(f)
        with open('trading_params.json', 'r') as f:
            params = json.load(f)
        
        # 2. Inicializar Firebase Admin SDK (Usando tu lógica de Service Account)
        # El Secret FIREBASE_CONFIG debe contener el JSON completo de la cuenta de servicio
        firebase_secret = os.environ.get('FIREBASE_CONFIG')
        if not firebase_admin._apps:
            cred_dict = json.loads(firebase_secret)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'
            })

        # 3. Obtener datos del mercado (EUR/USD por defecto)
        activo = params['monitoreo']['activos'][0]
        ticker = yf.Ticker(activo)
        df = ticker.history(period="1d", interval="1m").tail(5)
        
        if df.empty:
            print(f"❌ No se obtuvieron datos para {activo}")
            return

        precio_actual = df['Close'].iloc[-1]
        tipo_fvg, fvg_top, fvg_bottom = calcular_fvg(df)

        # 4. Lógica de Señal
        if tipo_fvg:
            fvg_msg = f"{'COMPRA' if tipo_fvg == 'BULLISH' else 'VENTA'}: FVG DETECTADO"
            bias = tipo_fvg
        else:
            fvg_msg = "SISTEMA OPERATIVO | ESCANEANDO..."
            bias = brain['estrategia']['bias_diario']

        # 5. Sincronización con Firebase (Método Administrativo)
        # .set() asegura que se cree la estructura aunque la base de datos esté en 'null'
        ref = db.reference('/') 
        ref.set({
            'precio': str(round(precio_actual, 5)),
            'fvg': fvg_msg,
            'fvg_top': float(fvg_top),
            'fvg_bottom': float(fvg_bottom), 
            'tendencia': bias,
            'riesgo': brain['configuracion']['riesgo'],
            'metodo': brain['estrategia']['metodo'],
            'last_update': datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"✅ SINCRO EXITOSA [{activo}]: {precio_actual} - {fvg_msg}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO DEL MOTOR: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
