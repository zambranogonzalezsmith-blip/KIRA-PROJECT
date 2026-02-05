import os
import asyncio
from metaapi_cloud_sdk import MetaApi
import pandas as pd

TOKEN = os.getenv('MT5_TOKEN')
ACCOUNT_ID = os.getenv('MT5_ACCOUNT_ID')

# Tu función HTML integrada
def generar_reporte_html(symbol, precio, rsi, estado):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kira Quantum Dashboard</title>
        <style>
            body {{ font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 20px; }}
            .card {{ background: #2d2d2d; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: inline-block; min-width: 300px; }}
            .status {{ font-size: 1.2em; font-weight: bold; color: #00ff88; }}
            .price {{ font-size: 2.5em; margin: 10px 0; color: #00d4ff; }}
            .info {{ color: #bbb; margin-bottom: 20px; }}
            .timestamp {{ font-size: 0.8em; color: #666; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Kira Quantum Live</h2>
            <p class="info">Activo: {symbol} | RSI: {rsi:.2f}</p>
            <div class="price">${precio}</div>
            <p class="status">Estado: {estado}</p>
            <hr style="border: 0.5px solid #444;">
            <p class="timestamp">Última actualización: {pd.Timestamp.now()}</p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

async def ejecutar_kira():
    api = MetaApi(TOKEN)
    try:
        account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
        await account.wait_connected()
        connection = account.get_rpc_connection()
        await connection.connect()

        symbol = 'XAUUSD' # Asegúrate que Just Markets use este nombre
        candles = await connection.get_candles(symbol, '15m', None, 20)
        df = pd.DataFrame(candles)
        
        # Cálculo simple de RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_actual = 100 - (100 / (1 + rs)).iloc[-1]
        precio_actual = df['close'].iloc[-1]
        
        estado = "Vigilando Mercado 💎"
        
        # Lógica de operación para capital pequeño
        if rsi_actual < 30:
            estado = "🚀 COMPRA ABIERTA"
            await connection.create_market_buy_order(symbol, 0.01, 30, 60)
        elif rsi_actual > 70:
            estado = "📉 VENTA ABIERTA"
            await connection.create_market_sell_order(symbol, 0.01, 30, 60)

        # Actualizamos el HTML con los datos reales
        generar_reporte_html(symbol, precio_actual, rsi_actual, estado)
        print(f"Dashboard actualizado: {precio_actual} - {estado}")

    except Exception as e:
        generar_reporte_html("Error", 0, 0, f"Error: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_kira())
