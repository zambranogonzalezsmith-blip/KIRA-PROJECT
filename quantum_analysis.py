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
    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()

        symbol = 'XAUUSD' # Oro es volátil, ideal para scalping pequeño
        candles = await connection.get_candles(symbol, '15m', None, 50)
        df = pd.DataFrame(candles)
        
        # Indicadores
        rsi = calcular_rsi(df['close']).iloc[-1]
        ema_20 = df['close'].rolling(window=20).mean().iloc[-1]
        precio_actual = df['close'].iloc[-1]

        print(f"🔍 Analizando {symbol}: Precio {precio_actual} | RSI {rsi:.2f} | EMA {ema_20:.2f}")

        # LÓGICA DE ENTRADA CONSERVADORA
        # Solo compra si el precio está barato (RSI < 35) Y la tendencia es alcista (Precio > EMA)
        if rsi < 35 and precio_actual > ema_20:
            print("🚀 COMPRA detectada: Ratio Riesgo/Beneficio 1:2")
            # 0.01 lotes, SL a 30 pips, TP a 60 pips
            await connection.create_market_buy_order(symbol, 0.01, 30, 60)

        # Solo vende si el precio está caro (RSI > 65) Y la tendencia es bajista (Precio < EMA)
        elif rsi > 65 and precio_actual < ema_20:
            print("📉 VENTA detectada: Protegiendo capital")
            await connection.create_market_sell_order(symbol, 0.01, 30, 60)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
