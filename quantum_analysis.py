import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

async def ejecutar_cerebro_quantum():
    if not TOKEN or not ACCOUNT_ID:
        print("[KIRA ERROR]: Faltan secretos MT5_TOKEN o MT5_ACCOUNT_ID.")
        return

    api = MetaApi(TOKEN)
    try:
        # Conexión al Broker (Admirals / Just Markets)
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        symbol = 'XAUUSD' # Activo principal: ORO
        
        # 1. Obtención de datos (Velas de 15 minutos)
        candles = await connection.get_candles(symbol, '15m', None, 50)
        df = pd.DataFrame(candles)

        # 2. Análisis Cuántico (Indicadores de Confluencia)
        df['RSI'] = ta.rsi(df['close'], length=14)
        df['EMA_20'] = ta.ema(df['close'], length=20)
        
        u_precio = df['close'].iloc[-1]
        u_rsi = df['RSI'].iloc[-1]
        u_ema = df['EMA_20'].iloc[-1]

        # Configuración de gestión de riesgo
        lote = 0.01
        sl_pips = 200  # Stop Loss
        tp_pips = 400  # Take Profit
        probabilidad = 0
        decision = "VIGILANDO"

        # 3. Lógica de Ejecución (Probabilidad > 80%)
        # COMPRA: RSI en zona baja + Precio rompiendo EMA hacia arriba
        if u_rsi < 45 and u_precio > u_ema:
            probabilidad = 85
            decision = "COMPRA ABIERTA"
            print(f"[KIRA]: Probabilidad {probabilidad}% - Ejecutando COMPRA en {symbol}")
            await connection.create_market_buy_order(symbol, lote, sl_pips, tp_pips)
            
        # VENTA: RSI en zona alta + Precio rompiendo EMA hacia abajo
        elif u_rsi > 55 and u_precio < u_ema:
            probabilidad = 85
            decision = "VENTA ABIERTA"
            print(f"[KIRA]: Probabilidad {probabilidad}% - Ejecutando VENTA en {symbol}")
            await connection.create_market_sell_order(symbol, lote, sl_pips, tp_pips)
        
        else:
            print(f"[KIRA]: Probabilidad baja. No se cumplen las condiciones de confluencia.")

        # 4. Generar Reporte para GitHub (README)
        fecha_act = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# 🌌 Kira Quantum System\n\n")
            f.write(f"### 🚀 Estado del Terminal\n")
            f.write(f"- **Última Actualización:** `{fecha_act}`\n")
            f.write(f"- **Cuenta:** `{ACCOUNT_ID}`\n")
            f.write(f"- **Estado de Kira:** `{decision}`\n\n")
            f.write(f"| Activo | Precio | RSI | EMA 20 | Probabilidad |\n")
            f.write(f"| :--- | :--- | :--- | :--- | :--- |\n")
            f.write(f"| {symbol} | {u_precio:.2f} | {u_rsi:.2f} | {u_ema:.2f} | {probabilidad}% |\n\n")
            f.write(f"--- \n*Kira Quantum opera bajo el linaje del Socio. Gestión de riesgo activa.*")

    except Exception as e:
        print(f"[KIRA ERROR]: Fallo en la matriz cuántica: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_cerebro_quantum())
