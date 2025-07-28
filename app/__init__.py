"""
Aplicación Streamlit del Chromabot System
Interfaz web para captura y análisis de datos RGB
"""

from .config import (
    PINEAPPLE_CODES, 
    MATURITY_STATES, 
    DATA_POINTS_TOTAL,
    DATA_POINTS_FILTERED,
    COLOR_SENSOR_CONFIG
)

__all__ = [
    'PINEAPPLE_CODES',
    'MATURITY_STATES', 
    'DATA_POINTS_TOTAL',
    'DATA_POINTS_FILTERED',
    'COLOR_SENSOR_CONFIG'
]