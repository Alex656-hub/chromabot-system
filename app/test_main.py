import streamlit as st

# Test básico para verificar que Streamlit funciona
st.title("🎨 Chromabot System - Test Básico")
st.write("Si ves este mensaje, Streamlit está funcionando correctamente.")

# Test de importaciones básicas
try:
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    st.success("✅ Librerías básicas importadas correctamente")
except Exception as e:
    st.error(f"❌ Error importando librerías básicas: {e}")

# Test de config
try:
    from config import PINEAPPLE_CODES, MATURITY_STATES
    st.success("✅ Configuración cargada correctamente")
    st.write(f"Tipos de piña disponibles: {len(PINEAPPLE_CODES)}")
    st.write(f"Estados de madurez: {len(MATURITY_STATES)}")
except Exception as e:
    st.error(f"❌ Error cargando configuración: {e}")

# Test de módulos src
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    from data_capture import RGBDataCapture
    st.success("✅ Módulo data_capture importado")
    
    from data_processing import RGBDataProcessor
    st.success("✅ Módulo data_processing importado")
    
    from export_utils import ChromabotExporter
    st.success("✅ Módulo export_utils importado")
    
except Exception as e:
    st.error(f"❌ Error importando módulos src: {e}")
    st.write("Información de debugging:")
    st.write(f"- Directorio actual: {os.getcwd()}")
    st.write(f"- Contenido directorio: {os.listdir('.')}")
    if os.path.exists('../src'):
        st.write(f"- Contenido src: {os.listdir('../src')}")

# Test básico de funcionalidad
st.header("🧪 Test de Funcionalidad Básica")

if st.button("Test Simulación RGB"):
    try:
        # Simular datos RGB
        import random
        r_values = [random.randint(100, 255) for _ in range(20)]
        g_values = [random.randint(80, 220) for _ in range(20)]
        b_values = [random.randint(60, 200) for _ in range(20)]
        
        # Mostrar datos
        st.write("Datos RGB simulados generados:")
        st.write(f"Promedio R: {sum(r_values)/len(r_values):.1f}")
        st.write(f"Promedio G: {sum(g_values)/len(g_values):.1f}")
        st.write(f"Promedio B: {sum(b_values)/len(b_values):.1f}")
        
        # Gráfico simple
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=r_values, name='Rojo', line=dict(color='red')))
        fig.add_trace(go.Scatter(y=g_values, name='Verde', line=dict(color='green')))
        fig.add_trace(go.Scatter(y=b_values, name='Azul', line=dict(color='blue')))
        fig.update_layout(title="Test RGB", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("✅ Test de simulación completado")
        
    except Exception as e:
        st.error(f"❌ Error en test de simulación: {e}")

# Información del sistema
st.header("💻 Información del Sistema")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")
st.write(f"Directorio de trabajo: {os.getcwd()}")

# Test final
st.success("🎉 Si llegaste hasta aquí, la configuración básica está funcionando!")
st.info("Ahora puedes probar el main.py principal o reportar los errores específicos que viste arriba.")