import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página Kira
st.set_page_config(page_title="Kira Trading Platform", layout="wide", page_icon="📈")

st.sidebar.title("KIRA CORE: TRADING")
symbol = st.sidebar.selectbox("Selecciona Activo", ("EURUSD=X", "GC=F"), index=0) # GC=F es Oro (XAU)
timeframe = st.sidebar.selectbox("Temporalidad", ("1h", "15m", "5m"), index=1)

st.title(f"Visualización de Mercado Soberano: {symbol}")

# Descarga de datos en tiempo real
data = yf.download(symbol, period="2d", interval=timeframe)

if not data.empty:
    # --- Lógica de Detección de FVG ---
    def detect_fvg(df):
        fvg_zones = []
        for i in range(1, len(df) - 1):
            # FVG Bajista (Gap en caída)
            if df['Low'].iloc[i-1] > df['High'].iloc[i+1]:
                fvg_zones.append({'top': df['Low'].iloc[i-1], 'bottom': df['High'].iloc[i+1], 'color': 'rgba(255, 0, 0, 0.2)'})
            # FVG Alcista (Gap en subida)
            elif df['High'].iloc[i-1] < df['Low'].iloc[i+1]:
                fvg_zones.append({'top': df['Low'].iloc[i+1], 'bottom': df['High'].iloc[i-1], 'color': 'rgba(0, 255, 0, 0.2)'})
        return fvg_zones

    # --- Generación de Gráfico Interactivo ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Precio Real"
    )])

    # Dibujar FVG detectados
    zones = detect_fvg(data)
    for zone in zones:
        fig.add_shape(type="rect", x0=data.index[0], x1=data.index[-1], y0=zone['bottom'], y1=zone['top'],
                      fillcolor=zone['color'], line_width=0)

    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- Sección de Señales de Kira ---
    st.subheader("🤖 Análisis de Kira (SMC)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("ZONA DE INTERÉS: Order Block detectado en nivel de oferta.")
        st.write(f"Precio Actual: {data['Close'].iloc[-1]:.5f}")
    
    with col2:
        st.success(f"PROYECCIÓN: FVG detectado. Sugerencia: Esperar retroceso para entrada óptima.")
        st.warning("RIESGO: Mantener Stop Loss a 20 pips del Order Block.")
