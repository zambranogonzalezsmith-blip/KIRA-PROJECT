# --- REEMPLAZA EL BLOQUE DE "ENVIAR A FIREBASE" POR ESTE ---

        # 4. Enviar a Firebase (Ruta Simplificada para asegurar conexión)
        # Usamos la raíz '/' para que los datos sean visibles de inmediato
        ref = db.reference('/') 
        ref.update({
            'precio': str(round(precio_actual, 5)),
            'fvg': fvg_msg,
            'fvg_top': float(fvg_top),    # Aseguramos que sea número
            'fvg_bottom': float(fvg_bottom), 
            'tendencia': bias,
            'riesgo': brain['configuracion']['riesgo'],
            'metodo': brain['estrategia']['metodo'],
            'last_update': datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"✅ DATOS SINCRONIZADOS: {precio_actual} - {fvg_msg}")
