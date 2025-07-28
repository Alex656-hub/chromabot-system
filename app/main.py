import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Chromabot Color System",
    page_icon="🎨",
    layout="wide"
)

# Importaciones con manejo de errores mejorado
try:
    from config import (
        PINEAPPLE_CODES, MATURITY_STATES, DATA_POINTS_TOTAL, 
        DATA_POINTS_FILTERED, COLOR_SENSOR_CONFIG, DATA_STRUCTURE
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Error cargando configuración: {e}")
    # Configuración de fallback
    PINEAPPLE_CODES = {"Golden (MD-2)": 1, "Roja Española": 2, "Cayena": 3}
    MATURITY_STATES = {"Verde": 1, "Madura": 2, "Sobre Madurada": 3}
    DATA_POINTS_TOTAL = 40
    DATA_POINTS_FILTERED = 20
    COLOR_SENSOR_CONFIG = {"model": "GY-31 TCS3200", "channels": ["R", "G", "B"]}
    CONFIG_AVAILABLE = False

# Importar módulos src con múltiples métodos de fallback
MODULES_AVAILABLE = False

# Método 1: Paquete instalado
try:
    from src import (
        RGBDataCapture, capture_rgb_sample,
        RGBDataProcessor, process_capture_session,
        ChromabotExporter, export_single_session_simple,
        initialize_color_sensor
    )
    MODULES_AVAILABLE = True
    MODULE_SOURCE = "paquete_instalado"
except ImportError:
    # Método 2: Path relativo
    try:
        import sys
        import os
        
        # Añadir src al path
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if os.path.exists(src_path):
            sys.path.insert(0, os.path.abspath(src_path))
        
        from data_capture import RGBDataCapture, capture_rgb_sample
        from data_processing import RGBDataProcessor, process_capture_session
        from export_utils import ChromabotExporter, export_single_session_simple
        from arduino_interface import initialize_color_sensor
        MODULES_AVAILABLE = True
        MODULE_SOURCE = "path_relativo"
    except ImportError as e:
        st.warning(f"⚠️ Módulos avanzados no disponibles: {e}")
        st.info("🎭 Continuando en modo básico...")
        MODULES_AVAILABLE = False
        MODULE_SOURCE = "no_disponible"

# Mostrar estado de carga
if not CONFIG_AVAILABLE:
    st.warning("⚠️ Usando configuración básica de fallback")

if MODULES_AVAILABLE:
    st.success(f"✅ Módulos cargados desde: {MODULE_SOURCE}")
else:
    st.info("🔧 Ejecutando en modo básico sin módulos avanzados")

# Título principal
st.title("🎨 Chromabot System - PROYECTO 1: RECOLECCIÓN DE COLOR")
st.subheader("Sistema de captura de datos RGB con sensor GY-31 TCS3200")

# Información del proyecto
st.info("📋 **Objetivo**: Recopilar dataset de valores RGB de piñas en diferentes estados de madurez")

# Resto del código continúa igual pero con validaciones...
st.divider()

# Inicialización del sistema (solo si módulos disponibles)
if MODULES_AVAILABLE and "capture_system" not in st.session_state:
    st.session_state.capture_system = RGBDataCapture()
    st.session_state.processor = RGBDataProcessor()
    st.session_state.exporter = ChromabotExporter()
    st.session_state.captured_sessions = []

# Sección de selección de tipo de piña
st.header("🍍 Selección de Tipo de Piña")

# Botones para tipo de piña
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🥇 Golden (MD-2)", use_container_width=True, type="primary"):
        st.session_state.pineapple_type = "Golden (MD-2)"
        st.session_state.pineapple_code = PINEAPPLE_CODES["Golden (MD-2)"]
        
with col2:
    if st.button("🔴 Roja Española", use_container_width=True, type="primary"):
        st.session_state.pineapple_type = "Roja Española"
        st.session_state.pineapple_code = PINEAPPLE_CODES["Roja Española"]
        
with col3:
    if st.button("🟡 Cayena", use_container_width=True, type="primary"):
        st.session_state.pineapple_type = "Cayena"
        st.session_state.pineapple_code = PINEAPPLE_CODES["Cayena"]

# Mostrar selección actual
if "pineapple_type" in st.session_state:
    st.success(f"✅ Tipo seleccionado: **{st.session_state.pineapple_type}**")
    st.info(f"🏷️ Código asignado: **{st.session_state.pineapple_code}**")
    
    # Selección de estado de madurez
    st.subheader("🌱 Estado de Madurez")
    maturity_state = st.selectbox(
        "Seleccione el estado de madurez:",
        options=list(MATURITY_STATES.keys()),
        index=0
    )
    
    if maturity_state:
        st.session_state.maturity_state = maturity_state
        st.session_state.maturity_code = MATURITY_STATES[maturity_state]
        st.info(f"📊 Estado: **{maturity_state}** (Código: {MATURITY_STATES[maturity_state]})")

st.divider()

# Botón de captura (siempre funcional)
if st.button("🚀 Iniciar Captura de Color", use_container_width=True, type="secondary"):
    if "pineapple_type" in st.session_state and "maturity_state" in st.session_state:
        
        if MODULES_AVAILABLE:
            # Usar sistema avanzado si está disponible
            st.info("🔄 Usando sistema avanzado...")
            try:
                session = capture_rgb_sample(
                    st.session_state.capture_system,
                    st.session_state.pineapple_type,
                    st.session_state.maturity_state,
                    notes="Captura web/GitHub"
                )
                if session:
                    st.success("✅ Captura avanzada completada!")
                    st.session_state.current_session = session
            except Exception as e:
                st.error(f"❌ Error en captura avanzada: {e}")
                MODULES_AVAILABLE = False  # Fallback al modo básico
        
        if not MODULES_AVAILABLE:
            # Modo básico siempre funcional
            st.info("🎭 Ejecutando captura simulada...")
            
            with st.spinner("Simulando captura RGB..."):
                progress_bar = st.progress(0)
                for i in range(20):
                    progress_bar.progress((i + 1) / 20)
                    time.sleep(0.1)
                
                # Generar datos simulados realistas
                r_values = np.random.randint(100, 255, DATA_POINTS_FILTERED).tolist()
                g_values = np.random.randint(80, 220, DATA_POINTS_FILTERED).tolist()
                b_values = np.random.randint(60, 200, DATA_POINTS_FILTERED).tolist()
                
                st.session_state.rgb_data = {
                    "r_values": r_values,
                    "g_values": g_values,
                    "b_values": b_values,
                    "r_avg": np.mean(r_values),
                    "g_avg": np.mean(g_values),
                    "b_avg": np.mean(b_values)
                }
            
            st.success("✅ Simulación completada!")
    else:
        st.error("⚠️ Por favor seleccione el tipo de piña y estado de madurez primero")

# Mostrar datos (siempre funcional)
if "rgb_data" in st.session_state:
    st.divider()
    st.header("📊 Datos RGB Capturados")
    
    data = st.session_state.rgb_data
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Rojo Promedio", f"{data['r_avg']:.1f}")
    with col2:
        st.metric("🟢 Verde Promedio", f"{data['g_avg']:.1f}")
    with col3:
        st.metric("🔵 Azul Promedio", f"{data['b_avg']:.1f}")
    
    # Gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data['r_values'], mode='lines+markers', name='Rojo', line=dict(color='red')))
    fig.add_trace(go.Scatter(y=data['g_values'], mode='lines+markers', name='Verde', line=dict(color='green')))
    fig.add_trace(go.Scatter(y=data['b_values'], mode='lines+markers', name='Azul', line=dict(color='blue')))
    
    fig.update_layout(
        title="Valores RGB Capturados",
        xaxis_title="Medición #",
        yaxis_title="Valor RGB",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Información del sistema
st.divider()
st.header("⚙️ Estado del Sistema")

status_data = {
    "Parámetro": [
        "Plataforma", "Configuración", "Módulos Avanzados", 
        "Modo de Captura", "Estado", "Timestamp"
    ],
    "Valor": [
        "Web/GitHub" if "codespace" in os.getcwd().lower() else "Local",
        "✅ OK" if CONFIG_AVAILABLE else "⚠️ Básica",
        f"✅ {MODULE_SOURCE}" if MODULES_AVAILABLE else "❌ No disponible",
        "Avanzado" if MODULES_AVAILABLE else "Simulación",
        "✅ Funcional",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
}

df_status = pd.DataFrame(status_data)
st.dataframe(df_status, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p><strong>Chromabot Color System v1.0</strong> - PROYECTO 1/3</p>
        <p>🎯 Sistema funcional en modo web</p>
    </div>
    """, 
    unsafe_allow_html=True
)