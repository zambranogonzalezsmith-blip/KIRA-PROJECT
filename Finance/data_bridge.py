import yfinance as yf
import time
import json
import os
import firebase_admin
from firebase_admin import credentials, db

# --- CONFIGURACIÓN PARA GITHUB ACTIONS ---
def conectar_firebase():
    # Recuperamos las credenciales desde las variables de entorno de GitHub
    firebase_json = os.environ.get('FIREBASE_CONFIG')
    if not firebase_json:
        print("❌ Error: No se encontró FIREBASE_CONFIG")
        return False
    
    cred_dict = json.loads(firebase_json)
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://kira-projet-default-rtdb.firebaseio.com'
        })
    return True

def enviar_datos():
    if not conectar_firebase(): return
    
    ticker = yf.Ticker("EURUSD=X")
    df = ticker.history(period="1d", interval="1m")
    
    if not df.empty:
        precio = round(df['Close'].iloc[-1], 5)
        fvg = "BULLISH" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "BEARISH"
        
        ref = db.reference('trading/EURUSD')
        ref.set({
            'precio': precio,
            'fvg': fvg,
            'tendencia': "ALCISTA" if precio > df['Open'].iloc[0] else "BAJISTA",
            'timestamp': time.strftime("%H:%M:%S")
        })
        print(f"📡 Kira envió: {precio}")

if __name__ == "__main__":
    enviar_datos()
