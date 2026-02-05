import os
import asyncio
from metaapi_cloud_sdk import MetaApi

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

async def ejecutar_cerebro_quantum():
    if not TOKEN or not ACCOUNT_ID:
        print("[KIRA ERROR]: Faltan las llaves de acceso en los Secrets de GitHub.")
        return

    api = MetaApi(TOKEN)
    try:
        # Localizamos la cuenta del Broker (Admirals o Just Markets)
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        
        # Esperamos a que la cuenta esté lista y conectada
        if account.state != 'DEPLOYED':
            print("[KIRA]: La cuenta no está desplegada en la nube. Iniciando...")
            await account.deploy()
        
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        # --- SECCIÓN DE ANÁLISIS ---
        print(f"[KIRA]: Conectada a la cuenta {ACCOUNT_ID}. Analizando flujo...")
        
        # Ejemplo: Obtener el precio actual del Oro (XAUUSD)
        symbol = 'XAUUSD'
        price = await connection.get_symbol_price(symbol)
        
        print(f"[KIRA]: Precio actual de {symbol}: {price['ask']}")
        
        # Aquí es donde pondremos tu lógica de Red Neuronal o RSI
        # Si decides comprar:
        # await connection.create_market_buy_order(symbol, 0.01)

    except Exception as e:
        print(f"[KIRA CRITICAL]: Fallo en la matriz: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_cerebro_quantum())
