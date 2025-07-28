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

# Configuración de captura de datos RGB
DATA_POINTS_TOTAL = 40      # Total de mediciones por muestra
DATA_POINTS_FILTERED = 20   # Los 20 datos centrales (descarta 10 inicial + 10 final)
START_INDEX = 10            # Índice donde inicia el filtrado
END_INDEX = 30              # Índice donde termina el filtrado

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
    "port": "COM3"  # Ajustar según puerto disponible
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
        "sample_id",           # ID único de muestra
        "pineapple_type",      # Tipo de piña
        "pineapple_code",      # Código numérico (1,2,3)
        "maturity_state",      # Estado de madurez
        "maturity_code",       # Código de madurez (1,2,3)
        "r_avg",              # Promedio canal Rojo
        "g_avg",              # Promedio canal Verde  
        "b_avg",              # Promedio canal Azul
        "r_values",           # Todos los valores R (20 datos)
        "g_values",           # Todos los valores G (20 datos)
        "b_values",           # Todos los valores B (20 datos)
        "timestamp",          # Fecha y hora de captura
        "measurement_notes"   # Notas adicionales
    ]
}