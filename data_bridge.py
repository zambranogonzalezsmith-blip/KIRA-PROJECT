import yfinance as yf
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime

def ejecutar_motor_kira():
    try:
        # 1. Cargar configuraciones locales
        with open('brain.json', 'r') as f:
            brain = json.load(f)
        with open('trading_params.json', 'r') as f:
            params = json.load(f)
        
        # 2. Inicialización con SDK Admin (Formato Moderno)
        firebase_config = os.environ.get('FIREBASE_CONFIG')
        if not firebase_admin._apps:
            # Convertimos el string del Secret en un diccionario real
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'
            })

        # 3. Obtención de datos reales (EUR/USD)
        ticker = yf.Ticker(params['monitoreo']['activos'][0])
        df = ticker.history(period="1d", interval="1m").tail(5)
        
        if df.empty:
            print("❌ Error: No hay datos de mercado.")
            return

        precio_actual = df['Close'].iloc[-1]

        # 4. Sincronización Directa a la Raíz
        # Usamos .set() para asegurar que sobreescriba el 'null' inicial
        ref = db.reference('/') 
        ref.set({
            'precio': str(round(precio_actual, 5)),
            'tendencia': brain['estrategia']['bias_diario'],
            'riesgo': brain['configuracion']['riesgo'],
            'last_update': datetime.now().strftime("%H:%M:%S"),
            'fvg': "SISTEMA OPERATIVO ✅"
        })
        
        print(f"🚀 MOTOR ACTUALIZADO: {precio_actual}")

    except Exception as e:
        print(f"❌ FALLO EN EL SDK ADMIN: {e}")

if __name__ == "__main__":
    ejecutar_motor_kira()
