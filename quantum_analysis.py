import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd

TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

def generar_reporte_html(symbol, precio, rsi, estado):
    # Generamos "Kira mt4.html" para que el Index.html lo cargue en el iframe
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; padding: 20px; }}
            .glow {{ text-shadow: 0 0 10px #00f2ff; color: #00f2ff; }}
            .panel {{ border: 1px solid #111; background: rgba(0, 242, 255, 0.02); padding: 20px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="panel">
            <h2 class="text-xs text-zinc-500 uppercase tracking-widest mb-4">>> Quantum Uplink Active</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <p class="text-[10px] text-cyan-500 uppercase">Asset / Price</p>
                    <p class="text-3xl font-bold glow">{symbol} / ${precio:,.2f}</p>
                </div>
                <div>
                    <p class="text-[10px] text-cyan-500 uppercase">Neural RSI</p>
                    <p class="text-3xl font-bold">{rsi:.2f}</p>
                </div>
            </div>
            <div class="mt-8 p-4 border-l-2 border-cyan-500 bg-cyan-500/5">
                <p class="text-sm font-bold tracking-tighter uppercase">{estado}</p>
            </div>
            <p class="text-[8px] text-zinc-700 mt-6 uppercase">Sync Time: {pd.Timestamp.now()}</p>
        </div>
    </body>
    </html>
    """
    # IMPORTANTE: El nombre del archivo debe coincidir con el que pusimos en el Index
    with open("Kira mt4.html", "w", encoding="utf-8") as f:
        f.write(html_content)

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
        
        # Cálculo manual de RSI (Sin librerías extra)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_actual = 100 - (100 / (1 + rs)).iloc[-1]
        precio_actual = df['close'].iloc[-1]
        
        estado = "Vigilando Mercado 💎"
        
        if rsi_actual < 30:
            estado = "🚀 COMPRA ABIERTA (0.01)"
            await connection.create_market_buy_order(symbol, 0.01, 30, 60)
        elif rsi_actual > 70:
            estado = "📉 VENTA ABIERTA (0.01)"
            await connection.create_market_sell_order(symbol, 0.01, 30, 60)

        generar_reporte_html(symbol, precio_actual, rsi_actual, estado)

    except Exception as e:
        generar_reporte_html("Error", 0, 0, f"Uplink Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
