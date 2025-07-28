"""
Chromabot System - Proyecto 1: Recolección de Color
Módulo de captura de datos RGB con sensor TCS3200

Funcionalidades:
- Captura sesiones completas RGB
- Validación calidad de datos
- Manejo robusto de errores  
- Modo simulación para testing
"""

import numpy as np
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import streamlit as st
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.config import (
    DATA_POINTS_TOTAL, DATA_POINTS_FILTERED, START_INDEX, END_INDEX,
    COLOR_SENSOR_CONFIG, PINEAPPLE_CODES, MATURITY_STATES
)

@dataclass
class RGBReading:
    """Estructura para una lectura RGB individual"""
    red: int
    green: int
    blue: int
    timestamp: datetime
    quality_score: float = 0.0

@dataclass
class CaptureSession:
    """Estructura para una sesión completa de captura"""
    sample_id: str
    pineapple_type: str
    pineapple_code: int
    maturity_state: str
    maturity_code: int
    raw_readings: List[RGBReading]
    filtered_readings: List[RGBReading]
    averages: Dict[str, float]
    statistics: Dict[str, Dict]
    capture_timestamp: datetime
    notes: str = ""
    is_simulation: bool = False

class RGBDataCapture:
    """
    Clase principal para manejo de captura de datos RGB
    """
    
    def __init__(self, arduino_interface=None):
        self.arduino = arduino_interface
        self.current_session = None
        self.quality_thresholds = {
            'min_value': 10,      # Valor mínimo RGB válido
            'max_value': 4000,    # Valor máximo RGB válido (para TCS3200)
            'std_threshold': 500, # Desviación estándar máxima aceptable
            'outlier_factor': 3   # Factor para detección outliers
        }
    
    def start_capture_session(self, pineapple_type: str, maturity_state: str, 
                            notes: str = "") -> bool:
        """
        Inicia una nueva sesión de captura
        """
        try:
            # Validar parámetros
            if pineapple_type not in PINEAPPLE_CODES:
                st.error(f"❌ Tipo de piña inválido: {pineapple_type}")
                return False
                
            if maturity_state not in MATURITY_STATES:
                st.error(f"❌ Estado de madurez inválido: {maturity_state}")
                return False
            
            # Generar ID único
            sample_id = self._generate_sample_id(pineapple_type, maturity_state)
            
            # Crear nueva sesión
            self.current_session = CaptureSession(
                sample_id=sample_id,
                pineapple_type=pineapple_type,
                pineapple_code=PINEAPPLE_CODES[pineapple_type],
                maturity_state=maturity_state,
                maturity_code=MATURITY_STATES[maturity_state],
                raw_readings=[],
                filtered_readings=[],
                averages={},
                statistics={},
                capture_timestamp=datetime.now(),
                notes=notes,
                is_simulation=self.arduino is None
            )
            
            st.success(f"✅ Sesión iniciada: {sample_id}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def capture_rgb_data(self) -> Optional[CaptureSession]:
        """
        Captura completa de datos RGB (40 mediciones → 20 filtradas)
        """
        if not self.current_session:
            st.error("❌ No hay sesión activa. Inicie una sesión primero.")
            return None
        
        try:
            if self.arduino and hasattr(self.arduino, 'is_connected') and self.arduino.is_connected:
                # Captura REAL con Arduino
                success = self._capture_real_data()
            else:
                # Captura SIMULADA
                success = self._capture_simulated_data()
            
            if success:
                # Procesar datos capturados
                self._process_captured_data()
                
                # Validar calidad
                if self._validate_data_quality():
                    st.success("✅ Captura completada con éxito")
                    return self.current_session
                else:
                    st.warning("⚠️ Captura completada pero con calidad cuestionable")
                    return self.current_session
            else:
                st.error("❌ Fallo en la captura de datos")
                return None
                
        except Exception as e:
            st.error(f"❌ Error durante captura: {e}")
            return None
    
    def _capture_real_data(self) -> bool:
        """Captura datos reales desde Arduino"""
        try:
            st.info("📡 Capturando con sensor TCS3200...")
            
            # Usar el método del arduino_interface
            filtered_data = self.arduino.capture_color_data()
            
            if not filtered_data:
                return False
            
            # Convertir datos del Arduino al formato interno
            self._convert_arduino_data(filtered_data)
            return True
            
        except Exception as e:
            st.error(f"❌ Error en captura real: {e}")
            return False
    
    def _capture_simulated_data(self) -> bool:
        """Captura datos simulados para testing"""
        try:
            st.info("🎭 Modo simulación - Generando datos RGB...")
            
            # Simular progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Generar 40 lecturas simuladas basadas en tipo de piña
            base_values = self._get_simulated_base_values()
            
            for i in range(DATA_POINTS_TOTAL):
                # Actualizar progreso
                progress = (i + 1) / DATA_POINTS_TOTAL
                progress_bar.progress(progress)
                status_text.text(f"Simulando lectura {i+1}/{DATA_POINTS_TOTAL}")
                
                # Generar lectura con ruido realista
                reading = self._generate_simulated_reading(base_values, i)
                self.current_session.raw_readings.append(reading)
                
                time.sleep(0.05)  # Simular tiempo de lectura real
            
            progress_bar.progress(1.0)
            status_text.text("✅ Simulación completada")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error en simulación: {e}")
            return False
    
    def _convert_arduino_data(self, arduino_data: Dict):
        """Convierte datos del Arduino al formato interno"""
        try:
            # Obtener valores filtrados del Arduino (ya son los 20 centrales)
            red_values = arduino_data.get("red", [])
            green_values = arduino_data.get("green", [])
            blue_values = arduino_data.get("blue", [])
            
            # Crear lecturas filtradas
            for i in range(len(red_values)):
                reading = RGBReading(
                    red=red_values[i],
                    green=green_values[i], 
                    blue=blue_values[i],
                    timestamp=datetime.now(),
                    quality_score=1.0  # Datos reales tienen calidad máxima
                )
                self.current_session.filtered_readings.append(reading)
            
            # Guardar promedios si vienen del Arduino
            if "averages" in arduino_data:
                self.current_session.averages = arduino_data["averages"]
            
        except Exception as e:
            st.error(f"❌ Error convirtiendo datos Arduino: {e}")
    
    def _get_simulated_base_values(self) -> Dict[str, int]:
        """Obtiene valores base simulados según tipo y estado de piña"""
        
        # Valores base por tipo de piña (basados en observación real)
        base_by_type = {
            "Golden (MD-2)": {"red": 1200, "green": 1000, "blue": 800},
            "Roja Española": {"red": 900, "green": 1100, "blue": 1000},
            "Cayena": {"red": 1100, "green": 950, "blue": 850}
        }
        
        # Modificadores por estado de madurez
        maturity_modifiers = {
            "Verde": {"red": 0.9, "green": 1.1, "blue": 1.0},
            "Madura": {"red": 1.0, "green": 1.0, "blue": 1.0},
            "Sobre Madurada": {"red": 1.2, "green": 0.9, "blue": 0.8}
        }
        
        base = base_by_type[self.current_session.pineapple_type]
        modifier = maturity_modifiers[self.current_session.maturity_state]
        
        return {
            "red": int(base["red"] * modifier["red"]),
            "green": int(base["green"] * modifier["green"]),
            "blue": int(base["blue"] * modifier["blue"])
        }
    
    def _generate_simulated_reading(self, base_values: Dict, index: int) -> RGBReading:
        """Genera una lectura simulada con ruido realista"""
        
        # Añadir ruido gaussiano más fuerte al inicio/final (por eso se filtran)
        if index < START_INDEX or index >= END_INDEX:
            noise_factor = 0.3  # 30% de ruido en extremos
        else:
            noise_factor = 0.1  # 10% de ruido en zona central
        
        red = max(50, int(np.random.normal(
            base_values["red"], 
            base_values["red"] * noise_factor
        )))
        
        green = max(50, int(np.random.normal(
            base_values["green"], 
            base_values["green"] * noise_factor
        )))
        
        blue = max(50, int(np.random.normal(
            base_values["blue"], 
            base_values["blue"] * noise_factor
        )))
        
        # Calcular score de calidad (mejor en zona central)
        if START_INDEX <= index < END_INDEX:
            quality_score = np.random.uniform(0.8, 1.0)
        else:
            quality_score = np.random.uniform(0.3, 0.7)
        
        return RGBReading(
            red=red,
            green=green,
            blue=blue,
            timestamp=datetime.now(),
            quality_score=quality_score
        )
    
    def _process_captured_data(self):
        """Procesa los datos capturados (filtrado y estadísticas)"""
        
        # Si tenemos datos raw, aplicar filtrado
        if self.current_session.raw_readings and not self.current_session.filtered_readings:
            self._apply_central_filtering()
        
        # Calcular estadísticas
        self._calculate_statistics()
        
        # Calcular promedios si no existen
        if not self.current_session.averages:
            self._calculate_averages()
    
    def _apply_central_filtering(self):
        """Aplica filtrado central (datos 10-30 de 40 totales)"""
        if len(self.current_session.raw_readings) >= DATA_POINTS_TOTAL:
            self.current_session.filtered_readings = self.current_session.raw_readings[START_INDEX:END_INDEX]
            st.info(f"🔄 Filtrado aplicado: {len(self.current_session.filtered_readings)} datos centrales")
    
    def _calculate_averages(self):
        """Calcula promedios RGB de datos filtrados"""
        if not self.current_session.filtered_readings:
            return
        
        red_vals = [r.red for r in self.current_session.filtered_readings]
        green_vals = [r.green for r in self.current_session.filtered_readings]
        blue_vals = [r.blue for r in self.current_session.filtered_readings]
        
        self.current_session.averages = {
            "red": np.mean(red_vals),
            "green": np.mean(green_vals),
            "blue": np.mean(blue_vals)
        }
    
    def _calculate_statistics(self):
        """Calcula estadísticas completas de los datos"""
        if not self.current_session.filtered_readings:
            return
        
        red_vals = [r.red for r in self.current_session.filtered_readings]
        green_vals = [r.green for r in self.current_session.filtered_readings]
        blue_vals = [r.blue for r in self.current_session.filtered_readings]
        
        self.current_session.statistics = {
            "red": {
                "mean": np.mean(red_vals),
                "std": np.std(red_vals),
                "min": np.min(red_vals),
                "max": np.max(red_vals),
                "median": np.median(red_vals)
            },
            "green": {
                "mean": np.mean(green_vals),
                "std": np.std(green_vals),
                "min": np.min(green_vals),
                "max": np.max(green_vals),
                "median": np.median(green_vals)
            },
            "blue": {
                "mean": np.mean(blue_vals),
                "std": np.std(blue_vals),
                "min": np.min(blue_vals),
                "max": np.max(blue_vals),
                "median": np.median(blue_vals)
            }
        }
    
    def _validate_data_quality(self) -> bool:
        """Valida la calidad de los datos capturados"""
        if not self.current_session.filtered_readings:
            return False
        
        quality_issues = []
        
        # Verificar valores en rango válido
        for reading in self.current_session.filtered_readings:
            if (reading.red < self.quality_thresholds['min_value'] or 
                reading.red > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor rojo fuera de rango: {reading.red}")
            
            if (reading.green < self.quality_thresholds['min_value'] or 
                reading.green > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor verde fuera de rango: {reading.green}")
            
            if (reading.blue < self.quality_thresholds['min_value'] or 
                reading.blue > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor azul fuera de rango: {reading.blue}")
        
        # Verificar desviación estándar
        stats = self.current_session.statistics
        for color in ['red', 'green', 'blue']:
            if stats[color]['std'] > self.quality_thresholds['std_threshold']:
                quality_issues.append(f"Alta variabilidad en {color}: std={stats[color]['std']:.1f}")
        
        # Mostrar issues encontrados
        if quality_issues:
            st.warning("⚠️ Issues de calidad detectados:")
            for issue in quality_issues[:5]:  # Mostrar máximo 5
                st.text(f"• {issue}")
            
            return len(quality_issues) <= 3  # Aceptable si hay 3 o menos issues
        
        return True
    
    def _generate_sample_id(self, pineapple_type: str, maturity_state: str) -> str:
        """Genera ID único para la muestra"""
        type_code = PINEAPPLE_CODES[pineapple_type]
        maturity_code = MATURITY_STATES[maturity_state]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"RGB_T{type_code}M{maturity_code}_{timestamp}"
    
    def get_session_summary(self) -> Optional[Dict]:
        """Retorna resumen de la sesión actual"""
        if not self.current_session:
            return None
        
        return {
            "sample_id": self.current_session.sample_id,
            "pineapple_info": f"{self.current_session.pineapple_type} ({self.current_session.maturity_state})",
            "total_readings": len(self.current_session.filtered_readings),
            "averages": self.current_session.averages,
            "capture_time": self.current_session.capture_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_simulation": self.current_session.is_simulation,
            "quality_passed": self._validate_data_quality() if self.current_session.filtered_readings else False
        }
    
    def reset_session(self):
        """Reinicia la sesión actual"""
        self.current_session = None
        st.info("🔄 Sesión reiniciada")

# Funciones de utilidad para uso en Streamlit
def initialize_capture_system(arduino_interface=None) -> RGBDataCapture:
    """Inicializa el sistema de captura"""
    return RGBDataCapture(arduino_interface)

def capture_rgb_sample(capture_system: RGBDataCapture, 
                      pineapple_type: str, 
                      maturity_state: str,
                      notes: str = "") -> Optional[CaptureSession]:
    """Función simplificada para capturar una muestra completa"""
    
    # Iniciar sesión
    if not capture_system.start_capture_session(pineapple_type, maturity_state, notes):
        return None
    
    # Capturar datos
    session = capture_system.capture_rgb_data()
    
    return session  

def main():
    """Función principal para testing desde línea de comandos"""
    print("🎨 Chromabot Data Capture - Test Mode")
    
    # Crear sistema de captura
    capture_system = RGBDataCapture()
    
    # Test básico
    if capture_system.start_capture_session("Golden (MD-2)", "Madura", "Test desde CLI"):
        print("✅ Sistema de captura inicializado correctamente")
        
        # Mostrar resumen
        summary = capture_system.get_session_summary()
        if summary:
            print(f"📊 ID: {summary['sample_id']}")
            print(f"🍍 Tipo: {summary['pineapple_info']}")
    else:
        print("❌ Error en inicialización")

if __name__ == "__main__":
    main()