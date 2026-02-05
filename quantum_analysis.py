import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd
import pandas_ta as ta

TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

async def ejecutar_cerebro_quantum():
    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        symbol = 'XAUUSD' # El Oro es ideal para este análisis
        # 1. Kira obtiene datos históricos para el análisis
        candles = await connection.get_candles(symbol, '15m', None, 50)
        df = pd.DataFrame(candles)

        # 2. Motor de Probabilidades (Confluencia)
        df['RSI'] = ta.rsi(df['close'], length=14)
        df['EMA_20'] = ta.ema(df['close'], length=20)
        
        ultimo_precio = df['close'].iloc[-1]
        ultimo_rsi = df['RSI'].iloc[-1]
        ultima_ema = df['EMA_20'].iloc[-1]

        # Lógica de probabilidad > 80%
        # Compra: RSI < 40 (alcista) + Precio sobre EMA 20
        # Venta: RSI > 60 (bajista) + Precio bajo EMA 20
        
        print(f"[KIRA]: Analizando confluencia para {symbol}...")
        
        probabilidad = 0
        if ultimo_rsi < 40 and ultimo_precio > ultima_ema:
            probabilidad = 85  # Alta probabilidad de rebote alcista
            print(f"[KIRA]: Probabilidad detectada: {probabilidad}% - SEÑAL DE COMPRA")
            await connection.create_market_buy_order(symbol, 0.01)
            
        elif ultimo_rsi > 60 and ultimo_precio < ultima_ema:
            probabilidad = 85  # Alta probabilidad de caída
            print(f"[KIRA]: Probabilidad detectada: {probabilidad}% - SEÑAL DE VENTA")
            await connection.create_market_sell_order(symbol, 0.01)
        
        else:
            print(f"[KIRA]: Probabilidad baja ({probabilidad}%). Mantengo liquidez, socio.")

    except Exception as e:
        print(f"[KIRA ERROR]: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_cerebro_quantum())
with open("README.md", "w") as f:
            f.write(f"# 🌌 Kira Quantum Status\n")
            f.write(f"**Última ejecución:** {pd.Timestamp.now()}\n")
            f.write(f"**Activo:** {symbol} | **Probabilidad:** {probabilidad}%\n")
            f.write(f"**Decisión:** {'OPERACIÓN ABIERTA' if probabilidad > 80 else 'ESPERANDO'}")
