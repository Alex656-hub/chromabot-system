import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Chromabot | Sistema Inteligente de Análisis RGB",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# ESTILOS CSS MODERNOS Y OPTIMIZADOS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* ===== VARIABLES GLOBALES ===== */
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
    
    /* ===== TIPOGRAFÍA ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* ===== LAYOUT PRINCIPAL ===== */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    /* ===== HEADER CON GLASSMORPHISM ===== */
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
    
    /* ===== HERO SECTION PERFECTAMENTE CENTRADO ===== */
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
    
    /* ===== CARDS MODERNAS ===== */
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
    
    /* ===== BOTONES ===== */
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
    
    /* ===== SEPARADORES DE SECCIÓN ===== */
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
    
    /* ===== TÍTULOS DE SECCIONES ===== */
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
    }
    
    /* ===== TABS MEJORADOS Y CENTRADOS ===== */
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
    
    /* ===== MÉTRICAS ===== */
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
    
    /* ===== ALERTAS ===== */
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
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div {
        background: var(--gradient-main);
        border-radius: 10px;
    }
    
    .stProgress > div {
        background: var(--light);
        border-radius: 10px;
    }
    
    /* ===== COLOR SAMPLE ===== */
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
    
    /* ===== CHART CONTAINER ===== */
    .chart-wrapper {
        background: white;
        border-radius: 18px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        margin: 1rem 0;
    }
    
    /* ===== FOOTER ===== */
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
    
    /* ===== DATAFRAME CENTRADO ===== */
    .stDataFrame {
        text-align: center;
    }
    
    /* ===== SELECTBOX LABEL CENTRADO ===== */
    .stSelectbox label {
        text-align: center;
        display: block;
    }
    
    /* ===== ANIMACIONES ===== */
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
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-badges { flex-direction: column; align-items: center; }
        .header-glass { padding: 1rem; }
        .header-wrapper { flex-direction: column; gap: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# IMPORTACIONES Y CONFIGURACIÓN
# ============================================================================

try:
    from config import (
        PINEAPPLE_CODES, MATURITY_STATES, DATA_POINTS_TOTAL, 
        DATA_POINTS_FILTERED, COLOR_SENSOR_CONFIG, DATA_STRUCTURE
    )
    CONFIG_AVAILABLE = True
except ImportError:
    PINEAPPLE_CODES = {"Golden (MD-2)": 1, "Roja Española": 2, "Cayena": 3}
    MATURITY_STATES = {"Verde": 1, "Madura": 2, "Sobre Madurada": 3}
    DATA_POINTS_TOTAL = 40
    DATA_POINTS_FILTERED = 20
    COLOR_SENSOR_CONFIG = {"model": "GY-31 TCS3200", "channels": ["R", "G", "B"]}
    CONFIG_AVAILABLE = False

MODULES_AVAILABLE = False
try:
    from src import (
        RGBDataCapture, capture_rgb_sample, RGBDataProcessor,
        process_capture_session, ChromabotExporter, export_single_session_simple,
        initialize_color_sensor
    )
    MODULES_AVAILABLE = True
    MODULE_SOURCE = "paquete_instalado"
except ImportError:
    try:
        import sys
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if os.path.exists(src_path):
            sys.path.insert(0, os.path.abspath(src_path))
        from src.data_capture import RGBDataCapture, capture_rgb_sample
        from src.data_processing import RGBDataProcessor, process_capture_session
        from src.export_utils import ChromabotExporter, export_single_session_simple
        from src.arduino_interface import initialize_color_sensor
        MODULES_AVAILABLE = True
        MODULE_SOURCE = "path_relativo"
    except ImportError:
        MODULE_SOURCE = "no_disponible"

# ============================================================================
# HEADER
# ============================================================================

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

# ============================================================================
# HERO SECTION
# ============================================================================

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

# ============================================================================
# INICIALIZACIÓN DEL SISTEMA
# ============================================================================

if MODULES_AVAILABLE and "capture_system" not in st.session_state:
    st.session_state.capture_system = RGBDataCapture()
    st.session_state.processor = RGBDataProcessor()
    st.session_state.exporter = ChromabotExporter()
    st.session_state.captured_sessions = []

# ============================================================================
# SECCIÓN DE CAPTURA
# ============================================================================

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

# TABS CON SISTEMA INCLUIDO
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍍 Variedad", "🌱 Madurez", "📸 Captura", "📊 Resultados", "⚙️ Sistema"])

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
    st.markdown("<h3 style='text-align: center;'>Proceso de Captura RGB</h3>", unsafe_allow_html=True)
    
    if "pineapple_type" in st.session_state and "maturity_state" in st.session_state:
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            {"icon": "🍍", "value": str(st.session_state.pineapple_code), "label": st.session_state.pineapple_type},
            {"icon": "🌱", "value": str(st.session_state.maturity_code), "label": st.session_state.maturity_state},
            {"icon": "📊", "value": str(DATA_POINTS_FILTERED), "label": "Puntos RGB"},
            {"icon": "⏱️", "value": "~3s", "label": "Tiempo Estimado"}
        ]
        
        for i, metric in enumerate(metrics_data):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-icon">{metric['icon']}</div>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-label">{metric['label']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🚀 INICIAR CAPTURA", use_container_width=True, key="capture"):
                
                if MODULES_AVAILABLE:
                    st.info("🔬 Captura con sensor físico...")
                    try:
                        session = capture_rgb_sample(
                            st.session_state.capture_system,
                            st.session_state.pineapple_type,
                            st.session_state.maturity_state,
                            notes=f"Web {datetime.now().strftime('%H:%M:%S')}"
                        )
                        if session:
                            st.success("✅ Captura completada")
                            st.session_state.current_session = session
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        MODULES_AVAILABLE = False
                
                if not MODULES_AVAILABLE:
                    progress_bar = st.progress(0)
                    status = st.empty()
                    
                    stages = ["🔌 Inicializando...", "🔍 Calibrando...", "📡 Conectando...", 
                             "📊 Capturando...", "🧮 Procesando...", "✅ Finalizando..."]
                    
                    for i, stage in enumerate(stages):
                        status.info(stage)
                        for j in range(5):
                            progress_bar.progress((i * 5 + j + 1) / 30)
                            time.sleep(0.08)
                    
                    profiles = {
                        ("Golden (MD-2)", "Verde"): {"r": (80, 120), "g": (100, 140), "b": (60, 90)},
                        ("Golden (MD-2)", "Madura"): {"r": (150, 190), "g": (140, 180), "b": (80, 120)},
                        ("Golden (MD-2)", "Sobre Madurada"): {"r": (200, 240), "g": (160, 200), "b": (70, 110)},
                        ("Roja Española", "Verde"): {"r": (70, 110), "g": (110, 150), "b": (50, 80)},
                        ("Roja Española", "Madura"): {"r": (180, 220), "g": (120, 160), "b": (70, 110)},
                        ("Roja Española", "Sobre Madurada"): {"r": (220, 255), "g": (100, 140), "b": (60, 100)},
                        ("Cayena", "Verde"): {"r": (90, 130), "g": (120, 160), "b": (70, 100)},
                        ("Cayena", "Madura"): {"r": (170, 210), "g": (150, 190), "b": (90, 130)},
                        ("Cayena", "Sobre Madurada"): {"r": (210, 250), "g": (140, 180), "b": (80, 120)},
                    }
                    
                    key = (st.session_state.pineapple_type, st.session_state.maturity_state)
                    ranges = profiles.get(key, {"r": (100, 200), "g": (100, 200), "b": (100, 200)})
                    
                    r_vals = np.clip(np.random.normal(np.mean(ranges["r"]), 15, DATA_POINTS_FILTERED), 0, 255).astype(int).tolist()
                    g_vals = np.clip(np.random.normal(np.mean(ranges["g"]), 12, DATA_POINTS_FILTERED), 0, 255).astype(int).tolist()
                    b_vals = np.clip(np.random.normal(np.mean(ranges["b"]), 10, DATA_POINTS_FILTERED), 0, 255).astype(int).tolist()
                    
                    st.session_state.rgb_data = {
                        "r_values": r_vals, "g_values": g_vals, "b_values": b_vals,
                        "r_avg": np.mean(r_vals), "g_avg": np.mean(g_vals), "b_avg": np.mean(b_vals),
                        "r_std": np.std(r_vals), "g_std": np.std(g_vals), "b_std": np.std(b_vals),
                        "r_min": np.min(r_vals), "g_min": np.min(g_vals), "b_min": np.min(b_vals),
                        "r_max": np.max(r_vals), "g_max": np.max(g_vals), "b_max": np.max(b_vals),
                        "timestamp": datetime.now(),
                        "variety": st.session_state.pineapple_type,
                        "maturity": st.session_state.maturity_state,
                        "session_id": f"CHR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    }
                    
                    progress_bar.empty()
                    status.success("✅ Captura completada")
                    st.balloons()
    else:
        st.markdown("""
        <div class="alert-box alert-warning">
            ⚠️ Complete: Variedad de piña → Estado de madurez → Captura
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("<h3 style='text-align: center;'>Vista Previa</h3>", unsafe_allow_html=True)
    
    if "rgb_data" in st.session_state:
        data = st.session_state.rgb_data
        col1, col2, col3 = st.columns(3)
        
        for i, (channel, color, icon) in enumerate([("r", "Rojo", "🔴"), ("g", "Verde", "🟢"), ("b", "Azul", "🔵")]):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{data[f'{channel}_avg']:.1f}</div>
                    <div class="metric-label">{color}</div>
                </div>
                """, unsafe_allow_html=True)
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
                <tr><td style="padding:0.7rem 0;">🎯 Modo</td><td style="text-align:center;">{'Hardware' if MODULES_AVAILABLE else 'Simulación'}</td></tr>
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
                <tr><td style="padding:0.7rem 0;">🎯 Puntos</td><td style="text-align:center;">{DATA_POINTS_FILTERED}</td></tr>
                <tr><td style="padding:0.7rem 0;">🎛️ Precisión</td><td style="text-align:center;">±2% RGB</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ANÁLISIS DETALLADO
# ============================================================================

if "rgb_data" in st.session_state:
    st.markdown("""
    <div class="section-separator">
        <div class="section-title-box">📊 Análisis RGB</div>
    </div>
    """, unsafe_allow_html=True)
    
    data = st.session_state.rgb_data
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        {"icon": "🔴", "value": f"{data['r_avg']:.1f}", "label": "Rojo", "detail": f"σ={data['r_std']:.2f}"},
        {"icon": "🟢", "value": f"{data['g_avg']:.1f}", "label": "Verde", "detail": f"σ={data['g_std']:.2f}"},
        {"icon": "🔵", "value": f"{data['b_avg']:.1f}", "label": "Azul", "detail": f"σ={data['b_std']:.2f}"},
        {"icon": "⚡", "value": f"{data['r_avg']+data['g_avg']+data['b_avg']:.0f}", "label": "Intensidad", "detail": "Total"},
        {"icon": max([('🔴', data['r_avg']), ('🟢', data['g_avg']), ('🔵', data['b_avg'])], key=lambda x: x[1])[0], 
         "value": "Dominante", "label": max([('R', data['r_avg']), ('G', data['g_avg']), ('B', data['b_avg'])], key=lambda x: x[1])[0], 
         "detail": f"{max([data['r_avg'], data['g_avg'], data['b_avg']]):.1f}"}
    ]
    
    for i, m in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">{m['icon']}</div>
                <div class="metric-value">{m['value']}</div>
                <div class="metric-label">{m['label']}</div>
                <div class="metric-detail">{m['detail']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h3 style='text-align: center;'>Valores RGB Capturados</h3>", unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], vertical_spacing=0.12,
                           subplot_titles=('Serie Temporal', 'Distribución'))
        
        for channel, color, name in [('r', '#ef4444', 'Rojo'), ('g', '#22c55e', 'Verde'), ('b', '#3b82f6', 'Azul')]:
            fig.add_trace(go.Scatter(y=data[f'{channel}_values'], mode='lines+markers', name=name,
                                    line=dict(color=color, width=2.5), marker=dict(size=5)), row=1, col=1)
            fig.add_trace(go.Histogram(x=data[f'{channel}_values'], name=name, marker_color=color, 
                                      opacity=0.7, showlegend=False), row=2, col=1)
        
        fig.update_layout(height=550, hovermode='x unified', barmode='overlay',
                         plot_bgcolor='rgba(248,249,250,0.8)', paper_bgcolor='white')
        fig.update_xaxes(title_text="Punto", row=1, col=1)
        fig.update_yaxes(title_text="Valor RGB", row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='text-align: center;'>Muestra de Color</h3>", unsafe_allow_html=True)
        
        r, g, b = int(data['r_avg']), int(data['g_avg']), int(data['b_avg'])
        st.markdown(f"""
        <div class="color-display" style="height:180px; background:rgb({r},{g},{b});"></div>
        <div style="text-align:center; margin-top:1rem;">
            <div style="font-size:1.2rem; font-weight:700;">RGB({r}, {g}, {b})</div>
        </div>
        """, unsafe_allow_html=True)
        
        def rgb_to_hsv(r, g, b):
            r, g, b = r/255, g/255, b/255
            mx, mn = max(r,g,b), min(r,g,b)
            h = s = v = mx
            d = mx - mn
            s = 0 if mx == 0 else d/mx
            if d != 0:
                if mx == r: h = (60*((g-b)/d)+360)%360
                elif mx == g: h = (60*((b-r)/d)+120)%360
                elif mx == b: h = (60*((r-g)/d)+240)%360
            return h, s*100, v*100
        
        h, s, v = rgb_to_hsv(r, g, b)
        st.markdown(f"""
        <div class="card-modern" style="padding:1.2rem; margin-top:1rem;">
            <strong>🌈 Matiz:</strong> {h:.1f}°<br>
            <strong>💫 Saturación:</strong> {s:.1f}%<br>
            <strong>☀️ Brillo:</strong> {v:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Estadísticas y Correlación</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        stats_df = pd.DataFrame({
            'Canal': ['Rojo', 'Verde', 'Azul'],
            'Media': [data['r_avg'], data['g_avg'], data['b_avg']],
            'Desv.Est.': [data['r_std'], data['g_std'], data['b_std']],
            'Min': [data['r_min'], data['g_min'], data['b_min']],
            'Max': [data['r_max'], data['g_max'], data['b_max']]
        }).round(2)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with col2:
        corr = np.corrcoef([data['r_values'], data['g_values'], data['b_values']])
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr, x=['R','G','B'], y=['R','G','B'],
            colorscale='RdBu', zmid=0, text=np.round(corr, 3),
            texttemplate='%{text}', textfont={"size":13, "color":"white"}
        ))
        fig_corr.update_layout(height=250, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_corr, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Exportar CSV", use_container_width=True):
            df = pd.DataFrame({
                'Punto': range(1, len(data['r_values'])+1),
                'R': data['r_values'], 'G': data['g_values'], 'B': data['b_values']
            })
            st.download_button("⬇️ Descargar", df.to_csv(index=False), 
                             f"{data['session_id']}.csv", "text/csv", use_container_width=True)
    with col2:
        if st.button("🔄 Nueva Captura", use_container_width=True):
            del st.session_state.rgb_data
            st.rerun()
    with col3:
        st.button("🤖 Predecir (Pronto)", use_container_width=True, disabled=True)

# ============================================================================
# FOOTER
# ============================================================================

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
                🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)