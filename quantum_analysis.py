import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd

TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

def calcular_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

async def ejecutar_kira():
    if not TOKEN or not ACCOUNT_ID:
        print("❌ Faltan Secrets en GitHub")
        return

    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        # Just Markets usualmente usa XAUUSD o GOLD. 
        symbol = 'XAUUSD' 
        candles = await connection.get_candles(symbol, '15m', None, 30)
        
        df = pd.DataFrame(candles)
        rsi_series = calcular_rsi(df['close'])
        rsi_actual = rsi_series.iloc[-1]
        precio_actual = df['close'].iloc[-1]

        print(f"📊 {symbol} | Precio: {precio_actual} | RSI: {rsi_actual:.2d}")

        if rsi_actual < 30:
            print("🚀 Señal de COMPRA")
            await connection.create_market_buy_order(symbol, 0.01, 200, 400)
        elif rsi_actual > 70:
            print("📉 Señal de VENTA")
            await connection.create_market_sell_order(symbol, 0.01, 200, 400)
        else:
            print("💎 Mercado neutral. Vigilando...")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
