import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Chromabot | Sistema Inteligente de Análisis RGB",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --dark: #0f172a;
        --light: #f8fafc;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --gradient-main: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
        --shadow-lg: 0 10px 24px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 40px rgba(0,0,0,0.12);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    .header-glass {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 2.5rem;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: var(--shadow-md);
        animation: slideDown 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .header-wrapper {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-box {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .logo-badge {
        background: var(--gradient-main);
        border-radius: 14px;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: var(--shadow-md);
    }
    
    .logo-title {
        background: var(--gradient-main);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
    }
    
    .status-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(16, 185, 129, 0.1);
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .hero-banner {
        background: var(--gradient-main);
        padding: 4.5rem 2rem;
        border-radius: 28px;
        text-align: center;
        color: white;
        margin-bottom: 3.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
        animation: fadeInScale 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hero-banner::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.12), transparent 60%),
                    radial-gradient(circle at 70% 80%, rgba(255,255,255,0.08), transparent 60%);
        animation: float 8s ease-in-out infinite;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 100%;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .hero-title {
        font-size: clamp(2.8rem, 5.5vw, 4.2rem);
        font-weight: 800;
        margin-bottom: 1.3rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
        text-align: center;
        width: 100%;
    }
    
    .hero-subtitle {
        font-size: clamp(1.15rem, 2.3vw, 1.4rem);
        font-weight: 500;
        opacity: 0.96;
        margin-bottom: 1.5rem;
        line-height: 1.5;
        text-align: center;
        width: 100%;
    }
    
    .hero-description {
        font-size: 1.05rem;
        opacity: 0.92;
        max-width: 820px;
        margin: 0 auto 2.5rem;
        line-height: 1.65;
        text-align: center;
        width: 100%;
    }
    
    .hero-badges {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
        width: 100%;
    }
    
    .badge-item {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        padding: 0.85rem 1.6rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .badge-item:hover {
        background: rgba(255, 255, 255, 0.28);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    
    .card-modern {
        background: white;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        height: 100%;
        text-align: center;
    }
    
    .card-modern:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary);
    }
    
    .card-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-main);
        transform: scaleX(0);
        transition: transform 0.35s ease;
    }
    
    .card-modern:hover::before {
        transform: scaleX(1);
    }
    
    .card-icon-box {
        width: 60px;
        height: 60px;
        background: var(--gradient-main);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.9rem;
        margin: 0 auto 1.3rem;
        box-shadow: var(--shadow-md);
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.9rem;
        letter-spacing: -0.01em;
        text-align: center;
    }
    
    .card-text {
        color: var(--text-secondary);
        line-height: 1.65;
        font-size: 0.98rem;
        text-align: center;
    }
    
    .stButton > button {
        background: var(--gradient-main);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.95rem 2.2rem;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
        letter-spacing: -0.01em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .section-separator {
        display: flex;
        align-items: center;
        margin: 3.5rem 0 2.5rem;
    }
    
    .section-separator::before,
    .section-separator::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
    }
    
    .section-title-box {
        background: white;
        padding: 0.9rem 2rem;
        border-radius: 50px;
        border: 1px solid var(--border);
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 2rem;
        box-shadow: var(--shadow-sm);
        letter-spacing: -0.02em;
    }
    
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
        background: white;
        padding: 0.6rem;
        border-radius: 14px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        justify-content: center;
        display: flex;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.9rem 1.4rem;
        transition: all 0.25s ease;
        flex-shrink: 0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--light);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-main);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .metric-box {
        background: white;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.8rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .metric-box:hover {
        transform: scale(1.04);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }
    
    .metric-icon {
        font-size: 2.8rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.08));
    }
    
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        background: var(--gradient-main);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        font-size: 0.98rem;
        font-weight: 600;
        color: var(--text-secondary);
    }
    
    .metric-detail {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 0.6rem;
        opacity: 0.85;
    }
    
    .alert-box {
        border-radius: 14px;
        border: 1px solid;
        padding: 1.4rem 1.6rem;
        margin: 1.4rem 0;
        backdrop-filter: blur(8px);
        animation: slideInLeft 0.4s ease-out;
        text-align: center;
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
        border-color: rgba(99, 102, 241, 0.3);
        color: var(--primary);
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.04) 100%);
        border-color: rgba(16, 185, 129, 0.3);
        color: var(--success);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.04) 100%);
        border-color: rgba(245, 158, 11, 0.3);
        color: var(--warning);
    }
    
    .stProgress > div > div {
        background: var(--gradient-main);
        border-radius: 10px;
    }
    
    .stProgress > div {
        background: var(--light);
        border-radius: 10px;
    }
    
    .color-display {
        border-radius: 18px;
        border: 2px solid var(--border);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .color-display::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.25) 50%, transparent 70%);
        animation: shimmer 2.5s infinite;
    }
    
    .color-display:hover {
        transform: scale(1.03);
        box-shadow: var(--shadow-xl);
    }
    
    .chart-wrapper {
        background: white;
        border-radius: 18px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        margin: 1rem 0;
    }
    
    .footer-box {
        background: var(--dark);
        color: white;
        padding: 3.5rem 2rem 2.5rem;
        border-radius: 28px 28px 0 0;
        margin-top: 4.5rem;
        position: relative;
    }
    
    .footer-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-main);
    }
    
    .footer-wrapper {
        max-width: 1400px;
        margin: 0 auto;
        text-align: center;
    }
    
    .stDataFrame {
        text-align: center;
    }
    
    .stSelectbox label {
        text-align: center;
        display: block;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInScale {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(180deg); }
    }
    
    @keyframes shimmer {
        from { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        to { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-badges { flex-direction: column; align-items: center; }
        .header-glass { padding: 1rem; }
        .header-wrapper { flex-direction: column; gap: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

try:
    from config import (
        PINEAPPLE_CODES, MATURITY_STATES, DATA_POINTS_TOTAL, 
        DATA_POINTS_PER_SECTION, MEASUREMENT_SECTIONS, SECTION_CONFIG,
        SECTION_STATES, COLOR_SENSOR_CONFIG, DATA_STRUCTURE, VALIDATION_CONFIG,
        ARDUINO_CONFIG
    )
    CONFIG_AVAILABLE = True
except ImportError:
    PINEAPPLE_CODES = {"Golden (MD-2)": 1, "Roja Española": 2, "Cayena": 3}
    MATURITY_STATES = {"Verde": 1, "Madura": 2, "Sobre Madurada": 3}
    DATA_POINTS_TOTAL = 60
    DATA_POINTS_PER_SECTION = 20
    MEASUREMENT_SECTIONS = ["MEDIA", "SUPERIOR", "INFERIOR"]
    COLOR_SENSOR_CONFIG = {"model": "GY-31 TCS3200", "channels": ["R", "G", "B"]}
    CONFIG_AVAILABLE = False

MODULES_AVAILABLE = False
MODULE_SOURCE = "no_disponible"

import sys
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if os.path.exists(src_path):
    abs_src_path = os.path.abspath(src_path)
    if abs_src_path not in sys.path:
        sys.path.insert(0, abs_src_path)

try:
    from src.data_capture import RGBDataCapture, capture_rgb_sample
    from src.data_processing import RGBDataProcessor, process_capture_session
    from src.export_utils import ChromabotExporter, export_single_session_simple
    from src.arduino_interface import initialize_color_sensor
    MODULES_AVAILABLE = True
    MODULE_SOURCE = "path_relativo"
except ImportError:
    try:
        from src import (
            RGBDataCapture, capture_rgb_sample, RGBDataProcessor,
            process_capture_session, ChromabotExporter, export_single_session_simple,
            initialize_color_sensor
        )
        MODULES_AVAILABLE = True
        MODULE_SOURCE = "paquete_instalado"
    except ImportError:
        MODULE_SOURCE = "no_disponible"

st.markdown("""
<div class="header-glass">
    <div class="header-wrapper">
        <div class="logo-box">
            <div class="logo-badge">🎨</div>
            <h1 class="logo-title">Chromabot</h1>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span style="font-weight: 600; color: var(--text-secondary); font-size: 0.95rem;">Sistema Activo</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div class="hero-content">
        <h1 class="hero-title">Sistema Chromabot AI</h1>
        <p class="hero-subtitle">
            Análisis RGB de Precisión para Clasificación Automática de Piñas
        </p>
        <p class="hero-description">
            Revolucione la agricultura con tecnología de punta. Sistema basado en sensores RGB de alta precisión 
            y algoritmos avanzados de machine learning para clasificación de frutas con exactitud superior al 95%.
        </p>
        <div class="hero-badges">
            <div class="badge-item">⚡ Tiempo Real</div>
            <div class="badge-item">🔬 Alta Precisión</div>
            <div class="badge-item">📊 Analytics</div>
            <div class="badge-item">🤖 IA Integrada</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if MODULES_AVAILABLE and "capture_system" not in st.session_state:
    st.session_state.capture_system = RGBDataCapture()
    st.session_state.processor = RGBDataProcessor()
    st.session_state.exporter = ChromabotExporter()
    st.session_state.captured_sessions = []
    st.session_state.sensor_connected = False
    st.session_state.capture_session_active = False
    st.session_state.completed_sections = []
    st.session_state.remaining_sections = MEASUREMENT_SECTIONS.copy()
    st.session_state.selected_section = MEASUREMENT_SECTIONS[0] if MEASUREMENT_SECTIONS else None
    st.session_state.current_session = None
    st.session_state.current_section = None
    st.session_state.last_captured_section = None
    st.session_state.capture_in_progress = False
    st.session_state.pending_sample_code = None
    st.session_state.next_sample_code = None
    st.session_state.next_sample_code_for = None
    st.session_state.force_capture_tab = False

if MODULES_AVAILABLE:
    with st.expander("🔌 Conexión del sensor Arduino", expanded=False):
        col_connect, col_status = st.columns([1, 1])
        with col_connect:
            if st.button("Conectar Sensor", use_container_width=True):
                sensor = initialize_color_sensor(ARDUINO_CONFIG.get("port", "COM3"))
                if sensor:
                    st.session_state.capture_system.arduino = sensor
                    st.session_state.sensor_connected = True
        with col_status:
            if st.session_state.get("sensor_connected") and getattr(st.session_state.capture_system.arduino, "is_connected", False):
                st.success("✅ Sensor conectado y listo")
            else:
                st.warning("⚠️ Sensor no conectado")

st.markdown("""
<div class="section-separator">
    <div class="section-title-box">🔬 Sistema de Captura</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="alert-box alert-info">
    <strong>🎯 Objetivo:</strong> Construcción del dataset más completo de valores RGB de piñas tropicales 
    para entrenamiento de modelos de clasificación de próxima generación. Meta: 500+ muestras científicas.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍍 Variedad", "🌱 Madurez", "📸 Captura", "📊 Resultados", "⚙️ Sistema"])

if st.session_state.get("force_capture_tab"):
    components.html(
        """
        <script>
        (function() {
            const selectors = ['button[data-baseweb="tab"]', 'button[role="tab"]'];
            const clickCaptureTab = () => {
                for (const selector of selectors) {
                    const tabButtons = window.parent.document.querySelectorAll(selector);
                    if (tabButtons && tabButtons.length >= 3) {
                        tabButtons[2].click();
                        return true;
                    }
                }
                return false;
            };
            if (!clickCaptureTab()) {
                setTimeout(clickCaptureTab, 200);
                setTimeout(clickCaptureTab, 400);
            }
        })();
        </script>
        """,
        height=0,
    )
    st.session_state.force_capture_tab = False

with tab1:
    st.markdown("<h3 style='text-align: center;'>Selección de Variedad de Piña</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    varieties = {
        "Golden (MD-2)": {"icon": "🥇", "desc": "Premium, dulce y aromática"},
        "Roja Española": {"icon": "🔴", "desc": "Tradicional, sabor intenso"},
        "Cayena": {"icon": "🟡", "desc": "Clásica, versátil y jugosa"}
    }
    
    for i, (variety, info) in enumerate(varieties.items()):
        with [col1, col2, col3][i]:
            if st.button(f"{info['icon']} {variety}", use_container_width=True, key=f"var_{i}"):
                st.session_state.pineapple_type = variety
                st.session_state.pineapple_code = PINEAPPLE_CODES[variety]
                st.rerun()
    
    if "pineapple_type" in st.session_state:
        st.markdown(f"""
        <div class="alert-box alert-success">
            ✅ <strong>Variedad:</strong> {st.session_state.pineapple_type}<br>
            🏷️ <strong>Código:</strong> {st.session_state.pineapple_code}
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h3 style='text-align: center;'>Estado de Madurez</h3>", unsafe_allow_html=True)
    
    if "pineapple_type" in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            maturity_state = st.selectbox(
                "Seleccione el estado de madurez:",
                options=list(MATURITY_STATES.keys()),
                index=0,
                key="maturity"
            )
        
        if maturity_state:
            st.session_state.maturity_state = maturity_state
            st.session_state.maturity_code = MATURITY_STATES[maturity_state]
            
            maturity_icons = {"Verde": "🟢", "Madura": "🟡", "Sobre Madurada": "🟠"}
            st.markdown(f"""
            <div class="alert-box alert-info">
                {maturity_icons[maturity_state]} <strong>Estado:</strong> {maturity_state} 
                | <strong>Código:</strong> {MATURITY_STATES[maturity_state]}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-box alert-warning">
            ⚠️ Primero seleccione la variedad de piña
        </div>
        """, unsafe_allow_html=True)

with tab3:
    
    if "pineapple_type" in st.session_state and "maturity_state" in st.session_state:
        
        session = st.session_state.capture_system.current_session if st.session_state.capture_system else None
        active_code = None
        if session and session.sample_id:
            active_code = session.sample_id
        elif st.session_state.get("pending_sample_code"):
            active_code = st.session_state.pending_sample_code

        if active_code:
            st.markdown(f"""
            <div class="alert-box alert-info" style="border-radius: 16px; display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <strong>📌 Código de piña activo:</strong> {active_code}
                </div>
                <div style="opacity:0.8;">Seleccione las tres secciones para esta misma piña</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box alert-warning" style="border-radius: 16px;">
                ⚠️ Inicie una captura para generar el código de la piña actual.
            </div>
            """, unsafe_allow_html=True)

        st.subheader("🧩 Seleccione la sección a capturar")
        if st.session_state.get("capture_session_active"):
            pending_sections = st.session_state.remaining_sections
            if not pending_sections:
                st.success("✅ Todas las secciones fueron capturadas para este código. Vaya a Resultados para revisar o reinicie para una nueva piña.")
                st.session_state.selected_section = None
            else:
                default_option = pending_sections[0]
                chosen_option = st.radio(
                    "Seleccione la siguiente sección para el mismo código de piña:",
                    options=pending_sections,
                    index=0,
                    horizontal=True
                )
                st.session_state.selected_section = chosen_option
                st.info(f"📌 Capturando código {st.session_state.current_session.sample_id if st.session_state.current_session else st.session_state.pending_sample_code}")
        else:
            chosen_option = st.selectbox(
                "Seleccione la sección inicial de captura:",
                options=MEASUREMENT_SECTIONS,
                index=0
            )
            st.session_state.selected_section = chosen_option

        if "capture_in_progress" in st.session_state and st.session_state.capture_in_progress:
            current_section = st.session_state.get('current_section', 'MEDIA')
            completed_sections = st.session_state.get('completed_sections', [])
            
            st.markdown("### 📍 Progreso de Captura por Secciones")
            
            cols = st.columns(len(MEASUREMENT_SECTIONS))
            
            for idx, section_name in enumerate(MEASUREMENT_SECTIONS):
                with cols[idx]:
                    config = SECTION_CONFIG[section_name]
                    
                    if section_name == current_section and section_name not in completed_sections:
                        state = SECTION_STATES["active"]
                    elif section_name in completed_sections:
                        state = SECTION_STATES["completed"]
                    else:
                        state = SECTION_STATES["pending"]
                    
                    st.markdown(f"""
                    <div style="background: {state['color']}; padding: 1.2rem; 
                                border-radius: 14px; text-align: center; 
                                border: 2px solid {'#22c55e' if state['label'] == 'Capturando' else '#e5e7eb'};">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{config['icon']}</div>
                        <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem; color: #1f2937;">
                            {section_name}
                        </div>
                        <div style="font-size: 2rem;">{state['icon']}</div>
                        <div style="font-size: 0.85rem; color: #6b7280; margin-top: 0.3rem;">
                            {state['label']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        def _start_capture(selected_sections, reset_session=True):
            capture_system = st.session_state.capture_system
            st.session_state.capture_in_progress = True
            st.session_state.current_section = selected_sections[0]

            try:
                if reset_session or capture_system.current_session is None:
                    if not capture_system.start_capture_session(
                        st.session_state.pineapple_type,
                        st.session_state.maturity_state,
                        notes=f"Web {datetime.now().strftime('%H:%M:%S')}"
                    ):
                        st.session_state.capture_in_progress = False
                        return
                    session = capture_system.current_session
                    if session:
                        st.session_state.pending_sample_code = session.sample_id

                session = capture_system.capture_rgb_data(
                    sections=selected_sections,
                    reset_session=reset_session
                )

                if session:
                    st.success("✅ Captura completada")
                    st.session_state.current_session = session
                    st.session_state.capture_session_active = True
                    if reset_session:
                        st.session_state.completed_sections = []
                    completed = st.session_state.completed_sections
                    for section in selected_sections:
                        if section not in completed:
                            completed.append(section)
                    st.session_state.remaining_sections = [
                        s for s in MEASUREMENT_SECTIONS if s not in completed
                    ]
                    st.session_state.last_captured_section = selected_sections[-1]
                    st.session_state.selected_section = (
                        st.session_state.remaining_sections[0]
                        if st.session_state.remaining_sections else None
                    )
                    st.balloons()
                    st.session_state.capture_in_progress = False
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.capture_in_progress = False

        if st.session_state.get("capture_session_active"):
            if st.session_state.remaining_sections:
                col1, col2 = st.columns([2,1])
                with col1:
                    if st.button("➡️ Capturar sección seleccionada", use_container_width=True, key="capture_section_next"):
                        selected_option = st.session_state.selected_section
                        if selected_option:
                            _start_capture([selected_option], reset_session=False)
                with col2:
                    if st.button("🔄 Reiniciar captura", use_container_width=True, key="reset_capture"):
                        st.session_state.capture_session_active = False
                        st.session_state.current_session = None
                        st.session_state.completed_sections = []
                        st.session_state.remaining_sections = MEASUREMENT_SECTIONS.copy()
                        st.session_state.capture_system.reset_session()
                        st.session_state.selected_section = MEASUREMENT_SECTIONS[0] if MEASUREMENT_SECTIONS else None
                        st.session_state.last_captured_section = None
                        st.rerun()
            else:
                if st.button("🔄 Reiniciar captura completa", use_container_width=True, key="reset_full_capture"):
                    st.session_state.capture_session_active = False
                    st.session_state.current_session = None
                    st.session_state.completed_sections = []
                    st.session_state.remaining_sections = MEASUREMENT_SECTIONS.copy()
                    st.session_state.capture_system.reset_session()
                    st.session_state.selected_section = MEASUREMENT_SECTIONS[0] if MEASUREMENT_SECTIONS else None
                    st.session_state.last_captured_section = None
                    st.rerun()
        else:
            col1, col2 = st.columns([2,1])
            with col1:
                if st.button("🚀 Iniciar captura", use_container_width=True, key="capture_start_initial"):
                    selected_option = st.session_state.selected_section
                    if selected_option:
                        _start_capture([selected_option], reset_session=True)
            with col2:
                if st.button("🔁 Capturar todas las secciones", use_container_width=True, key="capture_all_sections"):
                    _start_capture(MEASUREMENT_SECTIONS, reset_session=True)
        
        if "current_session" in st.session_state and st.session_state.current_session:
            session = st.session_state.current_session
            st.markdown("---")
            st.markdown("## 📋 Resumen rápido")
            st.info(f"Código activo: {session.sample_id} | Secciones capturadas: {len(session.section_data)}/3")
        else:
            st.markdown("""
            <div class="alert-box alert-info">
                ℹ️ Seleccione "Iniciar captura" para generar el código de piña y comenzar las mediciones.
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("<h3 style='text-align: center;'>Resultados</h3>", unsafe_allow_html=True)
    
    if "current_session" in st.session_state and st.session_state.current_session:
        session = st.session_state.current_session
        
        st.markdown("---")
        st.markdown("## 📋 Verificación de Datos Capturados")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **📝 Información de la Muestra**
            - **Código:** {session.sample_id}
            - **Variedad:** {session.pineapple_type}
            - **Estado:** {session.maturity_state}
            """)
        
        with col2:
            st.info(f"""
            **⏱️ Detalles de Captura**
            - **Fecha:** {session.capture_timestamp.strftime('%Y-%m-%d')}
            - **Hora:** {session.capture_timestamp.strftime('%H:%M:%S')}
            - **Total lecturas:** {len(session.all_readings)}
            - **Secciones:** {len(session.section_data)}
            """)
        
        st.markdown("### 📊 Estadísticas por Sección")
        
        for section_name in MEASUREMENT_SECTIONS:
            if section_name in session.section_data:
                section_data = session.section_data[section_name]
                config = SECTION_CONFIG[section_name]
                
                with st.expander(f"{config['icon']} {section_name} - {len(section_data.readings)} lecturas", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🔴 Rojo", 
                                 f"{section_data.averages['red']:.1f}",
                                 f"±{section_data.statistics['red']['std']:.1f}")
                    
                    with col2:
                        st.metric("🟢 Verde",
                                 f"{section_data.averages['green']:.1f}",
                                 f"±{section_data.statistics['green']['std']:.1f}")
                    
                    with col3:
                        st.metric("🔵 Azul",
                                 f"{section_data.averages['blue']:.1f}",
                                 f"±{section_data.statistics['blue']['std']:.1f}")
                    
                    with col4:
                        cv_status = "✅" if section_data.cv_percentage < VALIDATION_CONFIG["max_cv_percentage"] else "⚠️"
                        st.metric("📊 CV", 
                                 f"{section_data.cv_percentage:.2f}%",
                                 f"{cv_status}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Quality Score:** {section_data.quality_score:.1f}/1.0")
                    with col2:
                        st.write(f"**Outliers:** {section_data.outliers_count}")
                    with col3:
                        duration = (section_data.timestamp_end - section_data.timestamp_start).total_seconds()
                        st.write(f"**Duración:** {duration:.1f}s")
        
        st.markdown("### 📈 Comparación Visual entre Secciones")
        
        sections_list = list(session.section_data.keys())
        
        fig = go.Figure()
        
        for channel, color in [('red', '#ef4444'), ('green', '#22c55e'), ('blue', '#3b82f6')]:
            values = [session.section_data[s].averages[channel] for s in sections_list]
            stds = [session.section_data[s].statistics[channel]['std'] for s in sections_list]
            
            fig.add_trace(go.Bar(
                name=channel.upper(),
                x=sections_list,
                y=values,
                error_y=dict(type='data', array=stds),
                marker_color=color
            ))
        
        fig.update_layout(
            barmode='group',
            title="Promedios RGB por Sección (con desviación estándar)",
            xaxis_title="Sección",
            yaxis_title="Valor RGB",
            height=450,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📄 Vista Detallada de Lecturas")
        
        display_data = []
        for reading in session.all_readings[:15]:
            display_data.append({
                'Sección': reading.section,
                'Índice Sección': reading.section_index,
                'Índice Global': reading.global_index,
                'R': reading.red,
                'G': reading.green,
                'B': reading.blue,
                'Quality': f"{reading.quality_score:.2f}",
                'Timestamp': reading.timestamp.strftime('%H:%M:%S')
            })
        
        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        if len(session.all_readings) > 15:
            with st.expander(f"📄 Ver todas las {len(session.all_readings)} lecturas"):
                all_data = []
                for reading in session.all_readings:
                    all_data.append({
                        'Sección': reading.section,
                        'Idx_Secc': reading.section_index,
                        'Idx_Global': reading.global_index,
                        'R': reading.red,
                        'G': reading.green,
                        'B': reading.blue,
                        'Quality': f"{reading.quality_score:.2f}",
                        'Hora': reading.timestamp.strftime('%H:%M:%S.%f')[:-3]
                    })
                df_all = pd.DataFrame(all_data)
                st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)
        
        if len(session.section_data) == len(MEASUREMENT_SECTIONS):
            st.markdown("### 🎯 Acciones Disponibles")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("💾 GUARDAR DATOS", use_container_width=True, type="primary", key="save_btn"):
                    try:
                        exporter = ChromabotExporter()
                        filepath = exporter.export_single_session(session)

                        if filepath:
                            st.success(f"✅ Datos guardados exitosamente")
                            st.info(f"📁 Archivo: {os.path.basename(filepath)}")
                            st.balloons()
                            if st.button("➕ Medir otra piña", key="another"):
                                capture_system = st.session_state.get("capture_system")
                                if capture_system:
                                    capture_system.reset_session()
                                st.session_state.current_session = None
                                st.session_state.capture_session_active = False
                                st.session_state.completed_sections = []
                                st.session_state.remaining_sections = MEASUREMENT_SECTIONS.copy()
                                st.session_state.selected_section = MEASUREMENT_SECTIONS[0] if MEASUREMENT_SECTIONS else None
                                st.session_state.pending_sample_code = None
                                st.session_state.last_captured_section = None
                                st.session_state.capture_in_progress = False

                                pineapple_type = st.session_state.get("pineapple_type")
                                maturity_state = st.session_state.get("maturity_state")

                                if capture_system and pineapple_type and maturity_state:
                                    if capture_system.start_capture_session(
                                        pineapple_type,
                                        maturity_state,
                                        notes=f"Nueva piña {datetime.now().strftime('%H:%M:%S')}"
                                    ):
                                        st.session_state.pending_sample_code = capture_system.current_session.sample_id
                                    else:
                                        st.warning("⚠️ No se pudo iniciar la nueva sesión. Verifique la conexión del sensor.")
                                else:
                                    st.warning("⚠️ Seleccione variedad y madurez antes de medir otra piña.")

                                st.session_state.force_capture_tab = True
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error guardando: {e}")

            with col2:
                if st.button("🗑️ ELIMINAR Y DESCARTAR", use_container_width=True, key="delete_btn"):
                    if 'confirm_delete' not in st.session_state:
                        st.session_state.confirm_delete = False

                    if not st.session_state.confirm_delete:
                        st.session_state.confirm_delete = True
                        st.warning("⚠️ Presione nuevamente para confirmar eliminación")
                    else:
                        del st.session_state.current_session
                        st.session_state.confirm_delete = False
                        st.warning("🗑️ Datos eliminados")
                        time.sleep(1)
                        st.rerun()

            with col3:
                if st.button("🔄 REPETIR CAPTURA", use_container_width=True, key="repeat_btn"):
                    if 'current_session' in st.session_state:
                        del st.session_state.current_session

                    st.info("🔄 Reiniciando captura... Manteniendo variedad y estado de madurez")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("👀 Completa las secciones restantes para habilitar las acciones finales.")
    else:
        st.info("Complete la captura para ver resultados")

with tab5:
    st.markdown("<h3 style='text-align: center;'>Estado del Sistema</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        platform = "Codespaces" if "codespace" in os.getcwd().lower() else "Local"
        st.markdown(f"""
        <div class="card-modern">
            <h3 style="margin-bottom:1.2rem;">Configuración</h3>
            <table style="width:100%; text-align:center;">
                <tr><td style="padding:0.7rem 0;">🖥️ Plataforma</td><td style="text-align:center;">{platform}</td></tr>
                <tr><td style="padding:0.7rem 0;">⚙️ Config</td><td style="text-align:center;">{'✅ OK' if CONFIG_AVAILABLE else '⚠️ Básica'}</td></tr>
                <tr><td style="padding:0.7rem 0;">📦 Módulos</td><td style="text-align:center;">{f'✅ {MODULE_SOURCE}' if MODULES_AVAILABLE else '❌ No disp.'}</td></tr>
                <tr><td style="padding:0.7rem 0;">🎯 Modo</td><td style="text-align:center;">{'Hardware' if MODULES_AVAILABLE else 'Sin Hardware'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card-modern">
            <h3 style="margin-bottom:1.2rem;">Sensor RGB</h3>
            <table style="width:100%; text-align:center;">
                <tr><td style="padding:0.7rem 0;">🔬 Modelo</td><td style="text-align:center;">{COLOR_SENSOR_CONFIG['model']}</td></tr>
                <tr><td style="padding:0.7rem 0;">📊 Canales</td><td style="text-align:center;">{', '.join(COLOR_SENSOR_CONFIG['channels'])}</td></tr>
                <tr><td style="padding:0.7rem 0;">🎯 Puntos</td><td style="text-align:center;">{DATA_POINTS_TOTAL}</td></tr>
                <tr><td style="padding:0.7rem 0;">🎛️ Precisión</td><td style="text-align:center;">±2% RGB</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
<div class="footer-box">
    <div class="footer-wrapper">
        <div style="display:flex; align-items:center; justify-content:center; gap:1rem; margin-bottom:1.5rem;">
            <div style="background:var(--gradient-main); border-radius:12px; width:36px; height:36px; 
                        display:flex; align-items:center; justify-content:center;">🎨</div>
            <h3 style="background:var(--gradient-main); -webkit-background-clip:text; 
                       -webkit-text-fill-color:transparent; font-size:1.6rem; margin:0;">Chromabot</h3>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.15); padding-top:1.5rem;">
            <div style="opacity:0.85;">© 2025 Chromabot System | Fase 1/3 - Recolección de Datos</div>
            <div style="opacity:0.7; margin-top:0.8rem; font-size:0.9rem;">
                🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)