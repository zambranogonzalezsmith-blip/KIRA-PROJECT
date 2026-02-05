import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd
from datetime import datetime

TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

def actualizar_hub_hibrido(symbol, precio, rsi, estado):
    # Leemos tu HTML base (el diseño Cyberpunk)
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyectamos los datos en los contenedores específicos
    # Buscamos etiquetas que crearemos en el paso 2
    actualizado = html.replace("{{PRECIO}}", f"{precio:.2f}")
    actualizado = actualizado.replace("{{RSI}}", f"{rsi:.2f}")
    actualizado = actualizado.replace("{{ESTADO}}", estado)
    actualizado = actualizado.replace("{{TIME}}", datetime.now().strftime('%H:%M:%S'))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(actualizado)

async def ejecutar_kira():
    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()

        symbol = 'XAUUSD' 
        candles = await connection.get_candles(symbol, '15m', None, 20)
        df = pd.DataFrame(candles)
        
        # Cálculo de RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        precio = df['close'].iloc[-1]
        estado = "Vigilando"

        # Lógica de Trading (Capital Pequeño)
        if rsi_val < 30:
            await connection.create_market_buy_order(symbol, 0.01, 30, 60)
            estado = "Comprando 🚀"
        elif rsi_val > 70:
            await connection.create_market_sell_order(symbol, 0.01, 30, 60)
            estado = "Vendiendo 📉"

        actualizar_hub_hibrido(symbol, precio, rsi_val, estado)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
