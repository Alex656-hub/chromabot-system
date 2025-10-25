# Configuración del Sistema Chromabot - PROYECTO 1: RECOLECCIÓN DE COLOR
# Enfocado únicamente en captura de datos RGB con sensor GY-31 TCS3200

# Códigos de piñas según DOCX
PINEAPPLE_CODES = {
    "Golden (MD-2)": 1,
    "Roja Española": 2, 
    "Cayena": 3
}

# Estados de madurez según DOCX
MATURITY_STATES = {
    "Verde": 1,
    "Madura": 2,
    "Sobre Madurada": 3
}

# ============================================================================
# CONFIGURACIÓN DE CAPTURA POR SECCIONES (ACTUALIZADO)
# ============================================================================

# Configuración de mediciones por sección
DATA_POINTS_PER_SECTION = 20  # Mediciones por cada sección
MEASUREMENT_SECTIONS = ["MEDIA", "SUPERIOR", "INFERIOR"]  # Orden de captura
DATA_POINTS_TOTAL = len(MEASUREMENT_SECTIONS) * DATA_POINTS_PER_SECTION  # 60 total
# Cantidad de lecturas útiles tras filtrado (coincide con el firmware TCS3200)
DATA_POINTS_FILTERED = 20

# Configuración detallada de cada sección
SECTION_CONFIG = {
    "MEDIA": {
        "order": 1,
        "name_es": "Sección Media (Principal)",
        "description": "Centro de la piña - Zona de mayor representatividad",
        "icon": "🎯",
        "color": "#10b981",
        "instruction": "Posicione el sensor en el CENTRO de la piña",
        "range_start": 1,
        "range_end": 20
    },
    "SUPERIOR": {
        "order": 2,
        "name_es": "Sección Superior",
        "description": "Zona superior - Cercana a la corona",
        "icon": "⬆️",
        "color": "#3b82f6",
        "instruction": "Posicione el sensor en la PARTE SUPERIOR de la piña",
        "range_start": 21,
        "range_end": 40
    },
    "INFERIOR": {
        "order": 3,
        "name_es": "Sección Inferior",
        "description": "Zona inferior - Base de la piña",
        "icon": "⬇️",
        "color": "#f59e0b",
        "instruction": "Posicione el sensor en la PARTE INFERIOR de la piña",
        "range_start": 41,
        "range_end": 60
    }
}

# Estados de indicador visual
SECTION_STATES = {
    "pending": {"icon": "⚪", "color": "#f3f4f6", "label": "Pendiente"},
    "active": {"icon": "🟢", "color": "#d1fae5", "label": "Capturando"},
    "completed": {"icon": "✅", "color": "#bfdbfe", "label": "Completada"}
}

# Configuración específica del sensor de COLOR
COLOR_SENSOR_CONFIG = {
    "model": "GY-31 TCS3200",
    "rgb_range": (0, 255),
    "channels": ["R", "G", "B"],
    "measurement_zones": ["superior", "lateral_derecho", "lateral_izquierdo"],
    "average_readings": True
}

# Configuración de Arduino para COLOR
ARDUINO_CONFIG = {
    "baudrate": 9600,
    "timeout": 1,
    "port": "COM3"
}

# Configuración de exportación
EXPORT_CONFIG = {
    "excel_filename": "chromabot_color_data",
    "date_format": "%Y%m%d_%H%M%S",
    "sheet_name": "Color_Dataset"
}

# Estructura de datos de salida
DATA_STRUCTURE = {
    "columns": [
        "sample_id",
        "pineapple_type",
        "pineapple_code",
        "maturity_state",
        "maturity_code",
        "r_avg",
        "g_avg",
        "b_avg",
        "r_values",
        "g_values",
        "b_values",
        "timestamp",
        "measurement_notes"
    ]
}

# ============================================================================
# ESTRUCTURA DE DATOS ACTUALIZADA (CON SECCIONES)
# ============================================================================

DATA_STRUCTURE_V2 = {
    "version": "2.0",
    "columns": [
        "sample_id",
        "pineapple_type",
        "pineapple_code",
        "maturity_state",
        "maturity_code",
        "measurement_section",
        "section_reading_num",
        "global_reading_num",
        "r_value",
        "g_value",
        "b_value",
        "timestamp",
        "quality_score",
        "measurement_notes"
    ],
    "summary_columns": [
        "sample_id",
        "pineapple_type",
        "pineapple_code",
        "maturity_state",
        "maturity_code",
        "section_name",
        "r_avg_section",
        "g_avg_section",
        "b_avg_section",
        "r_std_section",
        "g_std_section",
        "b_std_section",
        "cv_percentage",
        "section_quality_score",
        "timestamp_start",
        "timestamp_end"
    ]
}

# Configuración de validación
VALIDATION_CONFIG = {
    "max_cv_percentage": 5.0,
    "min_quality_score": 70.0,
    "max_outliers_per_section": 3
}