import yfinance as yf
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime

def ejecutar_motor_kira():
    print("🧠 Kira Oracle: Sincronizando redes neurales...")
    
    # 1. CARGAR ARCHIVOS DE CONFIGURACIÓN
    try:
        with open('brain.json', 'r') as f:
            brain = json.load(f)
        with open('trading_params.json', 'r') as f:
            params = json.load(f)
        print("✅ Configuración cargada con éxito.")
    except Exception as e:
        print(f"❌ Error al leer archivos JSON: {e}")
        return

    # 2. CONECTAR A FIREBASE
    firebase_config = os.environ.get('FIREBASE_CONFIG')
    if not firebase_config:
        print("❌ Error: No existe el secreto FIREBASE_CONFIG.")
        return

    try:
        if not firebase_admin._apps:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'
            })
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return

    # 3. OBTENER DATOS REALES (EURUSD)
    try:
        ticker_symbol = params['monitoreo']['activos'][0] # Usa el primer activo del JSON
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="1d", interval="1m")
        if data.empty: raise ValueError("No hay datos de mercado")
        
        precio_actual = data['Close'].iloc[-1]
    except Exception as e:
        print(f"❌ Error de mercado: {e}")
        return

    # 4. LÓGICA DE DETECCIÓN (SIMULADA SMC)
    # Aquí es donde Kira aplica su "personalidad"
    bias = brain['estrategia']['bias_diario']
    fvg_detectado = "BUSCANDO LIQUIDEZ..."
    
    # Simulación lógica: Si el precio es mayor al cierre anterior, Kira busca compras
    if precio_actual > data['Open'].iloc[-1]:
        fvg_detectado = f"COMPRA {brain['estrategia']['indicadores'][0]} DETECTADO"
    else:
        fvg_detectado = f"VENTA {brain['estrategia']['indicadores'][0]} DETECTADO"

    # 5. ACTUALIZACIÓN INTEGRAL EN FIREBASE
    try:
        ref = db.reference('trading/EURUSD')
        ref.update({
            'precio': str(round(precio_actual, 5)),
            'fvg': fvg_detectado,
            'tendencia': bias,
            # Nuevos campos para tu nuevo index.html:
            'riesgo': brain['configuracion']['riesgo'],
            'metodo': brain['estrategia']['metodo'],
            'last_update': datetime.now().strftime("%H:%M:%S")
        })
        print(f"🚀 Kira ha materializado: {precio_actual} | {fvg_detectado}")
    except Exception as e:
        print(f"❌ Error al inyectar datos: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
