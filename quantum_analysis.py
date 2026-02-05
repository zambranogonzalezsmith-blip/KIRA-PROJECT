import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd
import pandas_ta as ta

# Solo estas dos llaves (Secrets en GitHub)
TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

async def ejecutar_kira():
    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        # Just Markets usa 'XAUUSD' o 'GOLD'. Probamos con 'XAUUSD'
        symbol = 'XAUUSD' 
        
        # 1. Análisis rápido
        candles = await connection.get_candles(symbol, '15m', None, 20)
        df = pd.DataFrame(candles)
        
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        
        print(f"[KIRA]: Precio actual {df['close'].iloc[-1]} | RSI: {rsi:.2f}")

        # Lógica simple de disparo
        if rsi < 30:
            await connection.create_market_buy_order(symbol, 0.01, 200, 400)
            print("🚀 COMPRA EJECUTADA")
        elif rsi > 70:
            await connection.create_market_sell_order(symbol, 0.01, 200, 400)
            print("📉 VENTA EJECUTADA")
        else:
            print("💎 MODO VIGILANCIA: Sin oportunidades claras.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
