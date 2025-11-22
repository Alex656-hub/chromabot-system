import numpy as np
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.config import (
    DATA_POINTS_TOTAL, DATA_POINTS_PER_SECTION, MEASUREMENT_SECTIONS,
    SECTION_CONFIG, COLOR_SENSOR_CONFIG, PINEAPPLE_CODES, MATURITY_STATES,
    VALIDATION_CONFIG
)

@dataclass
class RGBReading:
    """Lectura RGB con metadatos de posición y calidad"""
    red: int
    green: int
    blue: int
    timestamp: datetime
    section: str
    section_index: int
    global_index: int
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para exportación"""
        return {
            'red': self.red,
            'green': self.green,
            'blue': self.blue,
            'timestamp': self.timestamp,
            'section': self.section,
            'section_index': self.section_index,
            'global_index': self.global_index,
            'quality_score': self.quality_score
        }

@dataclass
class SectionData:
    """Datos y estadísticas de una sección de medición"""
    section_name: str
    readings: List[RGBReading]
    averages: Dict[str, float]
    statistics: Dict[str, Dict]
    quality_score: float
    cv_percentage: float
    timestamp_start: datetime
    timestamp_end: datetime
    outliers_count: int = 0
    
    def get_summary_dict(self) -> Dict[str, Any]:
        """Genera resumen para exportación"""
        return {
            'section_name': self.section_name,
            'r_avg': self.averages['red'],
            'g_avg': self.averages['green'],
            'b_avg': self.averages['blue'],
            'r_std': self.statistics['red']['std'],
            'g_std': self.statistics['green']['std'],
            'b_std': self.statistics['blue']['std'],
            'cv_percentage': self.cv_percentage,
            'quality_score': self.quality_score,
            'readings_count': len(self.readings),
            'outliers_count': self.outliers_count,
            'timestamp_start': self.timestamp_start,
            'timestamp_end': self.timestamp_end
        }

@dataclass
class CaptureSession:
    """Sesión de captura con múltiples secciones"""
    sample_id: str
    pineapple_type: str
    pineapple_code: int
    maturity_state: str
    maturity_code: int
    
    section_data: Dict[str, SectionData]
    all_readings: List[RGBReading]
    global_averages: Dict[str, float]
    global_statistics: Dict[str, Dict]
    overall_quality_score: float
    capture_timestamp: datetime
    notes: str = ""
    is_simulation: bool = False
    
    def get_section_names(self) -> List[str]:
        """Lista de secciones en orden"""
        return list(self.section_data.keys())
    
    def get_total_readings(self) -> int:
        """Total de lecturas capturadas"""
        return len(self.all_readings)
    
    def is_complete(self) -> bool:
        """Verifica si la captura está completa"""
        return len(self.all_readings) == DATA_POINTS_TOTAL

class RGBDataCapture:
    """Maneja la captura de datos RGB del sensor"""
    
    def __init__(self, arduino_interface=None):
        self.arduino = arduino_interface
        self.current_session = None
        self.quality_thresholds = {
            'min_value': 10,
            'max_value': 4000,
            'std_threshold': 500,
            'outlier_factor': 3
        }
    
    def start_capture_session(self, pineapple_type: str, maturity_state: str, 
                            notes: str = "") -> bool:
        """Inicia una nueva sesión de captura"""
        try:
            if pineapple_type not in PINEAPPLE_CODES:
                st.error(f"❌ Tipo de piña inválido: {pineapple_type}")
                return False
                
            if maturity_state not in MATURITY_STATES:
                st.error(f"❌ Estado de madurez inválido: {maturity_state}")
                return False
            
            sample_id = self._generate_sample_id(pineapple_type, maturity_state)
            
            self.current_session = CaptureSession(
                sample_id=sample_id,
                pineapple_type=pineapple_type,
                pineapple_code=PINEAPPLE_CODES[pineapple_type],
                maturity_state=maturity_state,
                maturity_code=MATURITY_STATES[maturity_state],
                section_data={},
                all_readings=[],
                global_averages={},
                global_statistics={},
                overall_quality_score=0.0,
                capture_timestamp=datetime.now(),
                notes=notes,
                is_simulation=False
            )
            
            st.success(f"✅ Sesión iniciada: {sample_id}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def capture_rgb_data(self, sections: Optional[List[str]] = None, reset_session: bool = True) -> Optional[CaptureSession]:
        """Captura datos RGB en múltiples secciones"""
        if not self.current_session:
            st.error("❌ No hay sesión activa. Inicie una sesión primero.")
            return None
        
        try:
            sections_to_capture = sections or MEASUREMENT_SECTIONS
            sections_to_capture = [section for section in sections_to_capture if section in SECTION_CONFIG]
            if not sections_to_capture:
                st.error("❌ No hay secciones válidas seleccionadas para capturar.")
                return None

            if not reset_session and self.current_session.section_data:
                pending_sections = [s for s in sections_to_capture if s not in self.current_session.section_data]
                if not pending_sections:
                    st.warning("⚠️ Las secciones seleccionadas ya fueron capturadas en esta sesión.")
                    return self.current_session
                sections_to_capture = pending_sections

            if self.arduino and hasattr(self.arduino, 'is_connected') and self.arduino.is_connected:
                success = self._capture_real_data(sections_to_capture, reset_session=reset_session)
            else:
                st.error("❌ Arduino no conectado. Conecte el sensor TCS3200 primero.")
                return None
            
            if success:
                self._process_captured_data()
                
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
    
    def _capture_real_data(self, sections: List[str], reset_session: bool = True) -> bool:
        """Captura datos reales desde Arduino con secciones"""
        try:
            st.info("📡 Iniciando captura con sensor TCS3200...")
            
            if reset_session or not self.current_session.section_data:
                self.current_session.all_readings = []
                self.current_session.section_data = {}
            
            for section_name in sections:
                section_config = SECTION_CONFIG[section_name]
                
                st.markdown(f"""
                <div style="background: {section_config['color']}; padding: 1rem; 
                            border-radius: 12px; margin: 1rem 0; text-align: center;">
                    <h3 style="margin: 0; color: white;">
                        {section_config['icon']} {section_config['name_es']}
                    </h3>
                    <p style="margin: 0.5rem 0 0; color: white; opacity: 0.9;">
                        {section_config['instruction']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(1)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                section_readings = []
                section_start_time = datetime.now()
                
                for i in range(DATA_POINTS_PER_SECTION):
                    section_idx = i + 1
                    global_idx = len(self.current_session.all_readings) + 1
                    
                    single_reading = self.arduino.get_single_reading()
                    
                    if not single_reading:
                        st.error(f"❌ Error leyendo datos del sensor en lectura {section_idx}")
                        return False
                    
                    reading = RGBReading(
                        red=single_reading.get('red', 0),
                        green=single_reading.get('green', 0),
                        blue=single_reading.get('blue', 0),
                        timestamp=datetime.now(),
                        section=section_name,
                        section_index=section_idx,
                        global_index=global_idx,
                        quality_score=1.0
                    )
                    
                    section_readings.append(reading)
                    self.current_session.all_readings.append(reading)
                    
                    progress = section_idx / DATA_POINTS_PER_SECTION
                    progress_bar.progress(progress)
                    status_text.text(
                        f"📊 {section_name}: Lectura {section_idx}/{DATA_POINTS_PER_SECTION} | "
                        f"RGB: ({reading.red}, {reading.green}, {reading.blue})"
                    )
                    
                    time.sleep(0.05)
                
                section_end_time = datetime.now()
                
                section_data = self._process_section_readings(
                    section_name, 
                    section_readings,
                    section_start_time,
                    section_end_time
                )
                
                self.current_session.section_data[section_name] = section_data
                
                progress_bar.empty()
                status_text.success(f"✅ Sección {section_name} completada: {len(section_readings)} lecturas")
                time.sleep(0.15)
            
            self._calculate_global_statistics()
            
            st.success(f"✅ Captura completada: {len(self.current_session.all_readings)} lecturas totales")
            return True
            
        except Exception as e:
            st.error(f"❌ Error en captura real: {e}")
            return False
    
    def _process_section_readings(self, section_name: str, 
                                 readings: List[RGBReading],
                                 start_time: datetime,
                                 end_time: datetime) -> SectionData:
        """Procesa las lecturas de una sección y calcula estadísticas"""
        
        red_vals = [r.red for r in readings]
        green_vals = [r.green for r in readings]
        blue_vals = [r.blue for r in readings]
        
        averages = {
            "red": np.mean(red_vals),
            "green": np.mean(green_vals),
            "blue": np.mean(blue_vals)
        }
        
        statistics = {
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
        
        cv_red = (statistics["red"]["std"] / statistics["red"]["mean"]) * 100 if statistics["red"]["mean"] > 0 else 0
        cv_green = (statistics["green"]["std"] / statistics["green"]["mean"]) * 100 if statistics["green"]["mean"] > 0 else 0
        cv_blue = (statistics["blue"]["std"] / statistics["blue"]["mean"]) * 100 if statistics["blue"]["mean"] > 0 else 0
        cv_percentage = np.mean([cv_red, cv_green, cv_blue])
        
        quality_scores = [r.quality_score for r in readings]
        section_quality = np.mean(quality_scores)
        
        outliers_count = 0
        for channel_vals in [red_vals, green_vals, blue_vals]:
            mean_val = np.mean(channel_vals)
            std_val = np.std(channel_vals)
            outliers = [v for v in channel_vals if abs(v - mean_val) > 3 * std_val]
            outliers_count += len(outliers)
        
        return SectionData(
            section_name=section_name,
            readings=readings,
            averages=averages,
            statistics=statistics,
            quality_score=section_quality,
            cv_percentage=cv_percentage,
            timestamp_start=start_time,
            timestamp_end=end_time,
            outliers_count=outliers_count
        )
    
    def _calculate_global_statistics(self):
        """Calcula estadísticas globales combinando todas las secciones"""
        
        if not self.current_session.all_readings:
            return
        
        all_red = [r.red for r in self.current_session.all_readings]
        all_green = [r.green for r in self.current_session.all_readings]
        all_blue = [r.blue for r in self.current_session.all_readings]
        
        self.current_session.global_averages = {
            "red": np.mean(all_red),
            "green": np.mean(all_green),
            "blue": np.mean(all_blue)
        }
        
        self.current_session.global_statistics = {
            "red": {
                "mean": np.mean(all_red),
                "std": np.std(all_red),
                "min": np.min(all_red),
                "max": np.max(all_red)
            },
            "green": {
                "mean": np.mean(all_green),
                "std": np.std(all_green),
                "min": np.min(all_green),
                "max": np.max(all_green)
            },
            "blue": {
                "mean": np.mean(all_blue),
                "std": np.std(all_blue),
                "min": np.min(all_blue),
                "max": np.max(all_blue)
            }
        }
        
        all_quality_scores = [r.quality_score for r in self.current_session.all_readings]
        self.current_session.overall_quality_score = np.mean(all_quality_scores)
    
    def _process_captured_data(self):
        """Procesa los datos capturados por secciones"""
        
        if not self.current_session.global_averages:
            self._calculate_global_statistics()
    
    def _validate_data_quality(self) -> bool:
        """Valida la calidad de los datos capturados"""
        if not self.current_session.all_readings:
            return False
        
        quality_issues = []
        
        for reading in self.current_session.all_readings:
            if (reading.red < self.quality_thresholds['min_value'] or 
                reading.red > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor rojo fuera de rango: {reading.red}")
            
            if (reading.green < self.quality_thresholds['min_value'] or 
                reading.green > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor verde fuera de rango: {reading.green}")
            
            if (reading.blue < self.quality_thresholds['min_value'] or 
                reading.blue > self.quality_thresholds['max_value']):
                quality_issues.append(f"Valor azul fuera de rango: {reading.blue}")
        
        for section_name, section_data in self.current_session.section_data.items():
            if section_data.cv_percentage > VALIDATION_CONFIG['max_cv_percentage']:
                quality_issues.append(
                    f"CV alto en {section_name}: {section_data.cv_percentage:.2f}%"
                )
        
        if quality_issues:
            st.warning("⚠️ Issues de calidad detectados:")
            for issue in quality_issues[:5]:
                st.text(f"• {issue}")
            
            return len(quality_issues) <= 3
        
        return True
    
    def _generate_sample_id(self, pineapple_type: str, maturity_state: str) -> str:
        """Genera ID único para la muestra con formato: RGB_TxMy_YYYYMMDD_0001
        
        El número secuencial final (0001) se obtiene del contador correspondiente.
        """
        type_code = PINEAPPLE_CODES[pineapple_type]
        maturity_code = MATURITY_STATES[maturity_state]
        date_part = datetime.now().strftime("%Y%m%d")
        
        # Obtener el siguiente número de secuencia para este tipo de piña y madurez
        sequence_key = f"T{type_code}M{maturity_code}"
        next_seq = self._get_next_sequence(sequence_key)
        
        return f"RGB_{sequence_key}_{date_part}_{next_seq:04d}"
        
    def _get_next_sequence(self, sequence_key: str) -> int:
        """Obtiene el siguiente número de secuencia para la clave dada"""
        # Este método debería implementar la lógica para obtener el siguiente número de secuencia
        # basado en la clave (ej: T1M2). Por ahora, devuelve un número fijo para pruebas.
        # En producción, esto debería leerse/actualizarse desde una base de datos o archivo.
        return 1  # Temporal: siempre comienza en 1
    
    def get_session_summary(self) -> Optional[Dict]:
        """Retorna resumen de la sesión actual"""
        if not self.current_session:
            return None
        
        return {
            "sample_id": self.current_session.sample_id,
            "pineapple_info": f"{self.current_session.pineapple_type} ({self.current_session.maturity_state})",
            "total_readings": len(self.current_session.all_readings),
            "sections": len(self.current_session.section_data),
            "averages": self.current_session.global_averages,
            "capture_time": self.current_session.capture_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "quality_passed": self._validate_data_quality() if self.current_session.all_readings else False
        }
    
    def reset_session(self):
        """Reinicia sesión"""
        self.current_session = None
        st.info("🔄 Sesión reiniciada")

def initialize_capture_system(arduino_interface=None) -> RGBDataCapture:
    """Inicializa sistema de captura"""
    return RGBDataCapture(arduino_interface)

def capture_rgb_sample(capture_system: RGBDataCapture, 
                      pineapple_type: str, 
                      maturity_state: str,
                      notes: str = "",
                      sections: Optional[List[str]] = None) -> Optional[CaptureSession]:
    """Captura muestra RGB completa"""
    
    if not capture_system.start_capture_session(pineapple_type, maturity_state, notes):
        return None
    
    session = capture_system.capture_rgb_data(sections=sections, reset_session=True)
    
    return session

def main():
    """Función principal"""
    print("🎨 Chromabot Data Capture - Test Mode")
    
    capture_system = RGBDataCapture()
    
    if capture_system.start_capture_session("Golden (MD-2)", "Madura", "Test desde CLI"):
        print("✅ Sistema de captura inicializado correctamente")
        
        summary = capture_system.get_session_summary()
        if summary:
            print(f"📊 ID: {summary['sample_id']}")
            print(f"🍍 Tipo: {summary['pineapple_info']}")
    else:
        print("❌ Error en inicialización")

if __name__ == "__main__":
    main()