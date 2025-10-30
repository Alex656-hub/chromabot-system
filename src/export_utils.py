import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import json
import zipfile
import hashlib
from pathlib import Path
import streamlit as st
import sys

def get_project_root() -> Path:
    """Encuentra la raíz del proyecto de manera confiable"""
    current_file = Path(__file__).resolve()
    
    search_path = current_file.parent
    max_levels = 5
    
    for _ in range(max_levels):
        if (search_path / "requirements.txt").exists() or \
           (search_path / "main.py").exists() or \
           (search_path / "app").is_dir():
            return search_path
        
        parent = search_path.parent
        if parent == search_path:
            break
        search_path = parent
    
    return current_file.parent.parent

PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT / "app"))

from app.config import (DATA_STRUCTURE, EXPORT_CONFIG, PINEAPPLE_CODES, 
                       MATURITY_STATES, COLOR_SENSOR_CONFIG, DATA_POINTS_PER_SECTION,
                       MEASUREMENT_SECTIONS, VALIDATION_CONFIG)

class ChromabotExporter:
    """
    Clase principal para exportación de datos del Chromabot
    """
    
    def __init__(self, base_path: str = None):
        """
        Inicializa el exportador con rutas absolutas corregidas
        
        Args:
            base_path: Ruta base personalizada (opcional)
        """
        self.project_root = get_project_root()
        
        if base_path is None:
            data_root = self.project_root / "data"
        else:
            data_root = Path(base_path)
        
        data_root.mkdir(parents=True, exist_ok=True)
        
        self.data_root = data_root
        self.excel_path = data_root / "exports"
        self.backup_path = data_root / "backups"
        self.reports_path = data_root / "reports" 
        self.samples_path = data_root / "samples"
        
        for path in [self.excel_path, self.backup_path, self.reports_path, self.samples_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.current_dataset = []
        self.export_log = []
        
        print(f"📁 ChromabotExporter inicializado:")
        print(f"   - Raíz proyecto: {self.project_root}")
        print(f"   - Datos raíz: {self.data_root}")  
        print(f"   - Excel: {self.excel_path}")
        print(f"   - Backups: {self.backup_path}")
        print(f"   - Reportes: {self.reports_path}")
        print(f"   - Muestras: {self.samples_path}")
        
        # Ruta del archivo de contadores de exportación por tipo+madurez
        self.counters_file = self.data_root / "export_counters.json"
    
    def _concise_base_from_sample(self, session_data: Any) -> Optional[str]:
        """Construye base corta: chromabot_RGB_TxMy_YYYYMMDD a partir de sample_id.
        Retorna None si no hay sample_id con el formato esperado.
        """
        sample_id = getattr(session_data, 'sample_id', None)
        if not sample_id:
            return None
        parts = str(sample_id).split('_')
        # Esperado: ["RGB", "TxMy", "YYYYMMDD", "HHMMSS"]
        if len(parts) >= 3:
            id_core = '_'.join(parts[:2])
            date_part = parts[2]
            return f"chromabot_{id_core}_{date_part}"
        return f"chromabot_{sample_id}"
    
    def _get_sequence_key(self, session_data: Any) -> Optional[str]:
        """Construye la clave de secuencia T{tipo}M{madurez} a partir de la sesión.
        Retorna None si no hay datos suficientes.
        """
        try:
            if hasattr(session_data, 'pineapple_code') and hasattr(session_data, 'maturity_code'):
                return f"T{int(session_data.pineapple_code)}M{int(session_data.maturity_code)}"
            # Soporte para dicts u otros formatos
            p_code = getattr(session_data, 'pineapple_code', None) or session_data.get('pineapple_code')
            m_code = getattr(session_data, 'maturity_code', None) or session_data.get('maturity_code')
            if p_code is not None and m_code is not None:
                return f"T{int(p_code)}M{int(m_code)}"
        except Exception:
            pass
        return None
    
    def _next_sequence_for_key(self, key: str) -> str:
        """Lee/actualiza el contador para la clave dada y retorna secuencia con 4 dígitos."""
        counters: Dict[str, int] = {}
        try:
            if self.counters_file.exists():
                with open(self.counters_file, 'r', encoding='utf-8') as f:
                    counters = json.load(f)
        except Exception:
            counters = {}
        
        current = int(counters.get(key, 0)) + 1
        counters[key] = current
        try:
            with open(self.counters_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, indent=2)
        except Exception:
            # Si falla la persistencia, igual devolvemos el número en memoria
            pass
        return f"{current:04d}"
    
    def _next_sequence_from_session(self, session_data: Any) -> Optional[str]:
        """Obtiene la secuencia 4 dígitos para la sesión (por tipo+madurez)."""
        key = self._get_sequence_key(session_data)
        if not key:
            return None
        return self._next_sequence_for_key(key)
    
    def export_single_session(self, session_data: Any, 
                            filename: Optional[str] = None,
                            include_raw_data: bool = True) -> Optional[str]:
        """
        Exporta una sola sesión a Excel
        
        Args:
            session_data: Datos de la sesión de captura
            filename: Nombre personalizado del archivo
            include_raw_data: Si incluir datos raw además de filtrados
            
        Returns:
            Ruta del archivo exportado o None si error
        """
        try:
            if hasattr(session_data, 'section_data') and session_data.section_data:
                st.info("📊 Detectado formato V2.0 con secciones. Exportando Excel completo...")
                return self.export_excel_multi_sheet_v2(session_data, filename)
            else:
                st.info("📊 Detectado formato V1.0. Exportando formato estándar...")
                export_data = self._prepare_session_data(session_data, include_raw_data)
                
                df = pd.DataFrame([export_data])
                
                if not filename:
                    seq = self._next_sequence_from_session(session_data)
                    base = self._concise_base_from_sample(session_data)
                    if not base:
                        # Fallback si no hay sample_id
                        date_only = datetime.now().strftime("%Y%m%d")
                        base = f"{EXPORT_CONFIG['excel_filename']}_{date_only}"
                    if seq:
                        filename = f"{base}_{seq}.xlsx"
                    else:
                        filename = f"{base}.xlsx"
                
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                
                filepath = self.excel_path / filename
                
                self._write_formatted_excel(df, filepath, single_session=True)
                
                self._log_export("single_session", filepath, 1)
                
                st.success(f"✅ Sesión exportada: {filename}")
                return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error exportando sesión: {e}")
            return None
    
    def export_multiple_sessions(self, sessions_data: List[Any], 
                               filename: Optional[str] = None,
                               include_summary: bool = True) -> Optional[str]:
        """
        Exporta múltiples sesiones a un solo archivo Excel
        
        Args:
            sessions_data: Lista de sesiones de captura
            filename: Nombre personalizado del archivo
            include_summary: Si incluir hoja de resumen
            
        Returns:
            Ruta del archivo exportado o None si error
        """
        try:
            if not sessions_data:
                st.warning("⚠️ No hay sesiones para exportar")
                return None
            
            export_data_list = []
            for session in sessions_data:
                export_data = self._prepare_session_data(session, include_raw_data=True)
                export_data_list.append(export_data)
            
            df_main = pd.DataFrame(export_data_list)
            
            if not filename:
                timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
                count = len(sessions_data)
                filename = f"{EXPORT_CONFIG['excel_filename']}_dataset_{count}samples_{timestamp}.xlsx"
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = self.excel_path / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_main.to_excel(writer, sheet_name=EXPORT_CONFIG["sheet_name"], 
                               index=False)
                
                if include_summary:
                    df_summary = self._create_summary_sheet(df_main)
                    df_summary.to_excel(writer, sheet_name="Resumen", index=False)
                
                df_metadata = self._create_metadata_sheet(sessions_data)
                df_metadata.to_excel(writer, sheet_name="Metadatos", index=False)
                
                self._apply_excel_formatting(writer, df_main)
            
            self._log_export("multiple_sessions", filepath, len(sessions_data))
            
            st.success(f"✅ {len(sessions_data)} sesiones exportadas: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error exportando múltiples sesiones: {e}")
            return None
    
    def export_dataset_for_ml(self, sessions_data: List[Any], 
                            include_features: bool = True) -> Optional[str]:
        """
        Exporta dataset optimizado para machine learning
        
        Args:
            sessions_data: Lista de sesiones
            include_features: Si incluir features extraídas
            
        Returns:
            Ruta del archivo exportado o None si error
        """
        try:
            from data_processing import RGBDataProcessor
            
            processor = RGBDataProcessor()
            ml_data = []
            
            for session in sessions_data:
                basic_data = self._prepare_session_data(session, include_raw_data=False)
                
                if include_features:
                    rgb_data = self._extract_rgb_from_session(session)
                    features = processor.extract_features(rgb_data)
                    basic_data.update(features)
                
                ml_data.append(basic_data)
            
            df_ml = pd.DataFrame(ml_data)
            
            timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
            filename = f"chromabot_ml_dataset_{len(sessions_data)}samples_{timestamp}.xlsx"
            filepath = self.excel_path / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_ml.to_excel(writer, sheet_name="ML_Dataset", index=False)
                
                df_variables = self._create_variable_dictionary(df_ml)
                df_variables.to_excel(writer, sheet_name="Variables", index=False)
                
                df_stats = self._create_descriptive_stats(df_ml)
                df_stats.to_excel(writer, sheet_name="Estadisticas", index=False)
            
            st.success(f"✅ Dataset ML exportado: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error exportando dataset ML: {e}")
            return None
    
    def create_backup(self, sessions_data: List[Any], 
                     backup_name: Optional[str] = None) -> Optional[str]:
        """
        Crea backup comprimido de los datos
        
        Args:
            sessions_data: Datos a respaldar
            backup_name: Nombre personalizado del backup
            
        Returns:
            Ruta del archivo de backup o None si error
        """
        try:
            timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
            
            if not backup_name:
                backup_name = f"chromabot_backup_{timestamp}"
            
            backup_file = self.backup_path / f"{backup_name}.zip"
            
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                temp_excel = self.export_multiple_sessions(sessions_data, 
                                                         f"temp_backup_{timestamp}")
                if temp_excel:
                    zipf.write(temp_excel, f"data_{timestamp}.xlsx")
                
                json_data = self._sessions_to_json(sessions_data)
                json_file = self.backup_path / f"temp_data_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, default=str)
                zipf.write(json_file, f"raw_data_{timestamp}.json")
                
                metadata = self._create_backup_metadata(sessions_data)
                metadata_file = self.backup_path / f"temp_metadata_{timestamp}.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, default=str)
                zipf.write(metadata_file, f"metadata_{timestamp}.json")
                
                for temp_file in [json_file, metadata_file]:
                    if temp_file.exists():
                        temp_file.unlink()
            
            checksum = self._calculate_file_checksum(backup_file)
            
            backup_info = {
                'filename': backup_file.name,
                'timestamp': timestamp,
                'sessions_count': len(sessions_data),
                'file_size': backup_file.stat().st_size,
                'checksum': checksum
            }
            
            info_file = self.backup_path / f"{backup_name}_info.json"
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            st.success(f"✅ Backup creado: {backup_file.name}")
            return str(backup_file)
            
        except Exception as e:
            st.error(f"❌ Error creando backup: {e}")
            return None
    
    def generate_report(self, sessions_data: List[Any]) -> Optional[str]:
        """
        Genera reporte estadístico del dataset
        
        Args:
            sessions_data: Datos para el reporte
            
        Returns:
            Ruta del archivo de reporte o None si error
        """
        try:
            from data_processing import RGBDataProcessor
            
            processor = RGBDataProcessor()
            report_data = {
                'general_info': self._analyze_dataset_general(sessions_data),
                'distribution_analysis': self._analyze_distribution(sessions_data),
                'quality_analysis': self._analyze_quality_overall(sessions_data),
                'statistical_summary': self._create_statistical_summary(sessions_data)
            }
            
            report_sections = []
            
            for key, value in report_data['general_info'].items():
                report_sections.append({
                    'Sección': 'Información General',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            for key, value in report_data['distribution_analysis'].items():
                report_sections.append({
                    'Sección': 'Análisis de Distribución',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            for key, value in report_data['quality_analysis'].items():
                report_sections.append({
                    'Sección': 'Análisis de Calidad',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            df_report = pd.DataFrame(report_sections)
            
            timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
            filename = f"chromabot_report_{timestamp}.xlsx"
            filepath = self.reports_path / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_report.to_excel(writer, sheet_name="Reporte", index=False)
                
                df_stats = pd.DataFrame(report_data['statistical_summary'])
                df_stats.to_excel(writer, sheet_name="Estadisticas_Detalladas", index=False)
            
            st.success(f"✅ Reporte generado: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            return None
    
    def _prepare_session_data(self, session_data: Any, 
                            include_raw_data: bool = True) -> Dict[str, Any]:
        """Prepara datos de sesión para exportación - VERSIÓN 2.0 CON SECCIONES"""
        
        if hasattr(session_data, 'section_data') and session_data.section_data:
            return self._prepare_session_data_v2(session_data, include_raw_data)
        else:
            return self._prepare_session_data_v1(session_data, include_raw_data)
    
    def _prepare_session_data_v2(self, session_data: Any, 
                                include_raw_data: bool = True) -> Dict[str, Any]:
        """Prepara datos con formato V2.0 (con secciones)"""
        
        basic_data = {
            'sample_id': session_data.sample_id,
            'pineapple_type': session_data.pineapple_type,
            'pineapple_code': session_data.pineapple_code,
            'maturity_state': session_data.maturity_state,
            'maturity_code': session_data.maturity_code,
            'capture_timestamp': session_data.capture_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'total_readings': len(session_data.all_readings),
            'measurement_notes': session_data.notes,
            'data_version': '2.0'
        }
        
        if session_data.global_averages:
            basic_data.update({
                'r_avg_global': session_data.global_averages['red'],
                'g_avg_global': session_data.global_averages['green'],
                'b_avg_global': session_data.global_averages['blue']
            })
        
        for section_name, section_data in session_data.section_data.items():
            prefix = section_name.lower()
            basic_data.update({
                f'{prefix}_r_avg': section_data.averages['red'],
                f'{prefix}_g_avg': section_data.averages['green'],
                f'{prefix}_b_avg': section_data.averages['blue'],
                f'{prefix}_r_std': section_data.statistics['red']['std'],
                f'{prefix}_g_std': section_data.statistics['green']['std'],
                f'{prefix}_b_std': section_data.statistics['blue']['std'],
                f'{prefix}_cv_pct': section_data.cv_percentage,
                f'{prefix}_quality': section_data.quality_score,
                f'{prefix}_outliers': section_data.outliers_count
            })
        
        if include_raw_data:
            for section_name, section_data in session_data.section_data.items():
                r_vals = [r.red for r in section_data.readings]
                g_vals = [r.green for r in section_data.readings]
                b_vals = [r.blue for r in section_data.readings]
                
                prefix = section_name.lower()
                basic_data.update({
                    f'{prefix}_r_values': str(r_vals),
                    f'{prefix}_g_values': str(g_vals),
                    f'{prefix}_b_values': str(b_vals)
                })
        
        return basic_data
    
    def _prepare_session_data_v1(self, session_data: Any, 
                                include_raw_data: bool = True) -> Dict[str, Any]:
        """Prepara datos con formato V1.0 (sin secciones) - BACKWARD COMPATIBILITY"""
        
        if hasattr(session_data, 'sample_id'):
            basic_data = {
                'sample_id': session_data.sample_id,
                'pineapple_type': session_data.pineapple_type,
                'pineapple_code': session_data.pineapple_code,
                'maturity_state': session_data.maturity_state,
                'maturity_code': session_data.maturity_code,
                'timestamp': session_data.capture_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'measurement_notes': session_data.notes,
                'data_version': '1.0'
            }
            
            if hasattr(session_data, 'filtered_readings') and session_data.filtered_readings:
                r_values = [r.red for r in session_data.filtered_readings]
                g_values = [r.green for r in session_data.filtered_readings]
                b_values = [r.blue for r in session_data.filtered_readings]
            else:
                r_values = g_values = b_values = []
            
            if session_data.averages:
                basic_data.update({
                    'r_avg': session_data.averages.get('red', 0),
                    'g_avg': session_data.averages.get('green', 0),
                    'b_avg': session_data.averages.get('blue', 0)
                })
            else:
                basic_data.update({
                    'r_avg': np.mean(r_values) if r_values else 0,
                    'g_avg': np.mean(g_values) if g_values else 0,
                    'b_avg': np.mean(b_values) if b_values else 0
                })
            
            if include_raw_data:
                basic_data.update({
                    'r_values': str(r_values),
                    'g_values': str(g_values),
                    'b_values': str(b_values),
                    'total_readings': len(r_values)
                })
            
            return basic_data
        else:
            return {
                'sample_id': session_data.get('sample_id', 'unknown'),
                'pineapple_type': session_data.get('pineapple_type', ''),
                'pineapple_code': session_data.get('pineapple_code', 0),
                'maturity_state': session_data.get('maturity_state', ''),
                'maturity_code': session_data.get('maturity_code', 0),
                'r_avg': session_data.get('r_avg', 0),
                'g_avg': session_data.get('g_avg', 0),
                'b_avg': session_data.get('b_avg', 0),
                'timestamp': session_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'measurement_notes': session_data.get('measurement_notes', ''),
                'data_version': '1.0'
            }
    
    def export_detailed_csv_with_sections(self, session_data: Any, 
                                         filename: Optional[str] = None) -> Optional[str]:
        """
        Exporta CSV detallado con todas las 60 lecturas y columna de sección
        
        Formato:
        codigo_pina,variedad,estado,fecha,hora,seccion,idx_seccion,idx_global,R,G,B,quality
        """
        
        try:
            if not hasattr(session_data, 'section_data') or not session_data.section_data:
                st.warning("⚠️ Datos sin secciones. Usando exportación estándar.")
                return self.export_single_session(session_data, filename)
            
            rows = []
            
            for reading in session_data.all_readings:
                rows.append({
                    'codigo_pina': session_data.sample_id,
                    'variedad': session_data.pineapple_type,
                    'variedad_codigo': session_data.pineapple_code,
                    'estado_madurez': session_data.maturity_state,
                    'madurez_codigo': session_data.maturity_code,
                    'fecha': reading.timestamp.strftime('%Y-%m-%d'),
                    'hora': reading.timestamp.strftime('%H:%M:%S'),
                    'seccion': reading.section,
                    'num_lectura_seccion': reading.section_index,
                    'num_lectura_global': reading.global_index,
                    'R': reading.red,
                    'G': reading.green,
                    'B': reading.blue,
                    'quality_score': f"{reading.quality_score:.3f}"
                })
            
            df = pd.DataFrame(rows)
            
            if not filename:
                seq = self._next_sequence_from_session(session_data)
                base_short = self._concise_base_from_sample(session_data)
                if base_short:
                    base = f"chromabot_detallado_{base_short.replace('chromabot_', '')}"
                else:
                    date_only = datetime.now().strftime("%Y%m%d")
                    base = f"chromabot_detallado_{date_only}"
                if seq:
                    filename = f"{base}_{seq}.csv"
                else:
                    filename = f"{base}.csv"
            
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            filepath = self.excel_path / filename
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            self._log_export("detailed_csv_sections", filepath, 1)
            
            st.success(f"✅ CSV detallado exportado: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error exportando CSV detallado: {e}")
            return None
    
    def export_excel_multi_sheet_v2(self, session_data: Any,
                                    filename: Optional[str] = None) -> Optional[str]:
        """
        Exporta Excel con 3 hojas:
        1. Datos_Completos: 60 lecturas con sección
        2. Resumen_Secciones: Estadísticas por sección
        3. Metadatos: Información de la medición
        """
        
        try:
            if not hasattr(session_data, 'section_data') or not session_data.section_data:
                st.warning("⚠️ Datos sin secciones. Usando exportación estándar.")
                return self.export_single_session(session_data, filename)
            
            if not filename:
                seq = self._next_sequence_from_session(session_data)
                base = self._concise_base_from_sample(session_data)
                if not base:
                    date_only = datetime.now().strftime("%Y%m%d")
                    base = f"chromabot_{date_only}"
                if seq:
                    filename = f"{base}_{seq}.xlsx"
                else:
                    filename = f"{base}.xlsx"
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = self.excel_path / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                rows_complete = []
                for reading in session_data.all_readings:
                    rows_complete.append({
                        'codigo_pina': session_data.sample_id,
                        'variedad': session_data.pineapple_type,
                        'var_codigo': session_data.pineapple_code,
                        'estado_madurez': session_data.maturity_state,
                        'mad_codigo': session_data.maturity_code,
                        'seccion': reading.section,
                        'idx_seccion': reading.section_index,
                        'idx_global': reading.global_index,
                        'R': reading.red,
                        'G': reading.green,
                        'B': reading.blue,
                        'quality': reading.quality_score,
                        'timestamp': reading.timestamp
                    })
                
                df_complete = pd.DataFrame(rows_complete)
                df_complete.to_excel(writer, sheet_name='Datos_Completos', index=False)
                
                rows_summary = []
                for section_name in MEASUREMENT_SECTIONS:
                    if section_name in session_data.section_data:
                        section = session_data.section_data[section_name]
                        rows_summary.append({
                            'codigo_pina': session_data.sample_id,
                            'seccion': section_name,
                            'lecturas': len(section.readings),
                            'R_promedio': section.averages['red'],
                            'R_std': section.statistics['red']['std'],
                            'R_min': section.statistics['red']['min'],
                            'R_max': section.statistics['red']['max'],
                            'G_promedio': section.averages['green'],
                            'G_std': section.statistics['green']['std'],
                            'G_min': section.statistics['green']['min'],
                            'G_max': section.statistics['green']['max'],
                            'B_promedio': section.averages['blue'],
                            'B_std': section.statistics['blue']['std'],
                            'B_min': section.statistics['blue']['min'],
                            'B_max': section.statistics['blue']['max'],
                            'CV_porcentaje': section.cv_percentage,
                            'quality_score': section.quality_score,
                            'outliers': section.outliers_count,
                            'hora_inicio': section.timestamp_start.strftime('%H:%M:%S'),
                            'hora_fin': section.timestamp_end.strftime('%H:%M:%S'),
                            'duracion_seg': (section.timestamp_end - section.timestamp_start).total_seconds()
                        })
                
                df_summary = pd.DataFrame(rows_summary)
                df_summary.to_excel(writer, sheet_name='Resumen_Secciones', index=False)
                
                metadata = {
                    'Campo': [
                        'Código Muestra',
                        'Variedad Piña',
                        'Código Variedad',
                        'Estado Madurez',
                        'Código Madurez',
                        'Fecha Captura',
                        'Hora Inicio',
                        'Hora Fin',
                        'Duración Total (seg)',
                        'Total Lecturas',
                        'Lecturas por Sección',
                        'Secciones Medidas',
                        'Sensor',
                        'Sistema',
                        'Versión Datos',
                        'Quality Score Global',
                        'Notas'
                    ],
                    'Valor': [
                        session_data.sample_id,
                        session_data.pineapple_type,
                        session_data.pineapple_code,
                        session_data.maturity_state,
                        session_data.maturity_code,
                        session_data.capture_timestamp.strftime('%Y-%m-%d'),
                        session_data.all_readings[0].timestamp.strftime('%H:%M:%S'),
                        session_data.all_readings[-1].timestamp.strftime('%H:%M:%S'),
                        (session_data.all_readings[-1].timestamp - session_data.all_readings[0].timestamp).total_seconds(),
                        len(session_data.all_readings),
                        DATA_POINTS_PER_SECTION,
                        ', '.join(MEASUREMENT_SECTIONS),
                        COLOR_SENSOR_CONFIG['model'],
                        'Chromabot System v2.0',
                        '2.0',
                        f"{session_data.overall_quality_score:.3f}",
                        session_data.notes
                    ]
                }
                
                df_metadata = pd.DataFrame(metadata)
                df_metadata.to_excel(writer, sheet_name='Metadatos', index=False)
            
            self._log_export("excel_multi_sheet_v2", filepath, 1)
            
            st.success(f"✅ Excel exportado con 3 hojas: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error exportando Excel: {e}")
            return None
    
    def _extract_rgb_from_session(self, session_data: Any) -> Dict[str, List[int]]:
        """Extrae valores RGB de una sesión"""
        if hasattr(session_data, 'all_readings'):
            return {
                'red': [r.red for r in session_data.all_readings],
                'green': [r.green for r in session_data.all_readings],
                'blue': [r.blue for r in session_data.all_readings]
            }
        elif hasattr(session_data, 'filtered_readings'):
            return {
                'red': [r.red for r in session_data.filtered_readings],
                'green': [r.green for r in session_data.filtered_readings],
                'blue': [r.blue for r in session_data.filtered_readings]
            }
        else:
            return {
                'red': session_data.get('r_values', []),
                'green': session_data.get('g_values', []),
                'blue': session_data.get('b_values', [])
            }
    
    def _write_formatted_excel(self, df: pd.DataFrame, filepath: Path, 
                             single_session: bool = False):
        """Escribe Excel con formato profesional"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=EXPORT_CONFIG["sheet_name"], index=False)
            
            workbook = writer.book
            worksheet = writer.sheets[EXPORT_CONFIG["sheet_name"]]
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _apply_excel_formatting(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Aplica formato avanzado a Excel"""
        workbook = writer.book
        
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            
            for row in range(2, len(df) + 2):
                if row % 2 == 0:
                    for col in range(1, len(df.columns) + 1):
                        cell = worksheet.cell(row=row, column=col)
    
    def _create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea hoja de resumen estadístico"""
        summary_data = []
        
        pineapple_counts = df['pineapple_type'].value_counts()
        for ptype, count in pineapple_counts.items():
            summary_data.append({
                'Categoría': 'Tipo de Piña',
                'Valor': ptype,
                'Cantidad': count,
                'Porcentaje': f"{(count/len(df)*100):.1f}%"
            })
        
        maturity_counts = df['maturity_state'].value_counts()
        for mstate, count in maturity_counts.items():
            summary_data.append({
                'Categoría': 'Estado Madurez',
                'Valor': mstate,
                'Cantidad': count,
                'Porcentaje': f"{(count/len(df)*100):.1f}%"
            })
        
        return pd.DataFrame(summary_data)
    
    def _create_metadata_sheet(self, sessions_data: List[Any]) -> pd.DataFrame:
        """Crea hoja de metadatos del experimento"""
        metadata = []
        
        metadata.extend([
            {'Parámetro': 'Proyecto', 'Valor': 'Chromabot - Recolección de Color'},
            {'Parámetro': 'Sensor', 'Valor': COLOR_SENSOR_CONFIG['model']},
            {'Parámetro': 'Fecha Exportación', 'Valor': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {'Parámetro': 'Total Muestras', 'Valor': str(len(sessions_data))},
            {'Parámetro': 'Canales RGB', 'Valor': ', '.join(COLOR_SENSOR_CONFIG['channels'])}
        ])
        
        metadata.append({'Parámetro': '--- CÓDIGOS PIÑA ---', 'Valor': ''})
        for ptype, code in PINEAPPLE_CODES.items():
            metadata.append({'Parámetro': f'Código {code}', 'Valor': ptype})
        
        metadata.append({'Parámetro': '--- CÓDIGOS MADUREZ ---', 'Valor': ''})
        for mstate, code in MATURITY_STATES.items():
            metadata.append({'Parámetro': f'Código {code}', 'Valor': mstate})
        
        return pd.DataFrame(metadata)
    
    def _create_variable_dictionary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea diccionario de variables para ML"""
        variables = []
        
        for column in df.columns:
            var_info = {
                'Variable': column,
                'Tipo': str(df[column].dtype),
                'Descripción': self._get_variable_description(column),
                'Valores_Únicos': df[column].nunique(),
                'Valores_Nulos': df[column].isnull().sum(),
                'Rango': f"{df[column].min()} - {df[column].max()}" if df[column].dtype in ['int64', 'float64'] else 'N/A'
            }
            variables.append(var_info)
        
        return pd.DataFrame(variables)
    
    def _get_variable_description(self, column: str) -> str:
        """Obtiene descripción de variable"""
        descriptions = {
            'sample_id': 'Identificador único de muestra',
            'pineapple_type': 'Tipo de piña (Golden, Roja, Cayena)',
            'pineapple_code': 'Código numérico del tipo (1-3)',
            'maturity_state': 'Estado de madurez (Verde, Madura, Sobre Madurada)',
            'maturity_code': 'Código numérico de madurez (1-3)',
            'r_avg_global': 'Promedio global canal Rojo',
            'g_avg_global': 'Promedio global canal Verde',
            'b_avg_global': 'Promedio global canal Azul',
            'media_r_avg': 'Promedio sección MEDIA - Rojo',
            'superior_r_avg': 'Promedio sección SUPERIOR - Rojo',
            'inferior_r_avg': 'Promedio sección INFERIOR - Rojo',
            'timestamp': 'Fecha y hora de captura',
        }
        
        return descriptions.get(column, f'Variable {column}')
    
    def _create_descriptive_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea estadísticas descriptivas"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        stats_df = df[numeric_columns].describe()
        
        stats_df = stats_df.transpose()
        stats_df.reset_index(inplace=True)
        stats_df.rename(columns={'index': 'Variable'}, inplace=True)
        
        return stats_df
    
    def _sessions_to_json(self, sessions_data: List[Any]) -> List[Dict]:
        """Convierte sesiones a formato JSON"""
        json_data = []
        
        for session in sessions_data:
            if hasattr(session, 'sample_id'):
                session_dict = {
                    'sample_id': session.sample_id,
                    'pineapple_type': session.pineapple_type,
                    'pineapple_code': session.pineapple_code,
                    'maturity_state': session.maturity_state,
                    'maturity_code': session.maturity_code,
                    'capture_timestamp': session.capture_timestamp.isoformat(),
                    'notes': session.notes,
                    'global_averages': session.global_averages,
                    'global_statistics': session.global_statistics,
                }
                
                if hasattr(session, 'all_readings'):
                    session_dict['all_readings'] = [
                        {
                            'red': r.red,
                            'green': r.green,
                            'blue': r.blue,
                            'section': r.section,
                            'section_index': r.section_index,
                            'global_index': r.global_index,
                            'timestamp': r.timestamp.isoformat(),
                            'quality_score': r.quality_score
                        } for r in session.all_readings
                    ]
            else:
                session_dict = dict(session)
            
            json_data.append(session_dict)
        
        return json_data
    
    def _create_backup_metadata(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Crea metadatos para backup"""
        return {
            'backup_info': {
                'created': datetime.now().isoformat(),
                'chromabot_version': '2.0',
                'project': 'Recolección de Color',
                'total_sessions': len(sessions_data)
            },
            'sensor_config': COLOR_SENSOR_CONFIG,
            'classification_codes': {
                'pineapple_codes': PINEAPPLE_CODES,
                'maturity_states': MATURITY_STATES
            }
        }
    
    def _calculate_file_checksum(self, filepath: Path) -> str:
        """Calcula checksum MD5 del archivo"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _analyze_dataset_general(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Análisis general del dataset"""
        total_sessions = len(sessions_data)
        
        type_counts = {}
        maturity_counts = {}
        
        for session in sessions_data:
            if hasattr(session, 'pineapple_type'):
                ptype = session.pineapple_type
                mstate = session.maturity_state
            else:
                ptype = session.get('pineapple_type', 'Unknown')
                mstate = session.get('maturity_state', 'Unknown')
            
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
            maturity_counts[mstate] = maturity_counts.get(mstate, 0) + 1
        
        return {
            'total_muestras': total_sessions,
            'tipos_piña': type_counts,
            'estados_madurez': maturity_counts
        }
    
    def _analyze_distribution(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Análisis de distribución del dataset"""
        all_r = []
        all_g = []
        all_b = []
        
        for session in sessions_data:
            rgb_data = self._extract_rgb_from_session(session)
            all_r.extend(rgb_data['red'])
            all_g.extend(rgb_data['green'])
            all_b.extend(rgb_data['blue'])
        
        return {
            'total_mediciones': len(all_r),
            'rango_rojo': f"{min(all_r)} - {max(all_r)}" if all_r else "N/A",
            'rango_verde': f"{min(all_g)} - {max(all_g)}" if all_g else "N/A",
            'rango_azul': f"{min(all_b)} - {max(all_b)}" if all_b else "N/A",
            'promedio_rojo': np.mean(all_r) if all_r else 0,
            'promedio_verde': np.mean(all_g) if all_g else 0,
            'promedio_azul': np.mean(all_b) if all_b else 0
        }
    
    def _analyze_quality_overall(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Análisis de calidad general"""
        quality_scores = []
        
        for session in sessions_data:
            if hasattr(session, 'overall_quality_score'):
                quality_scores.append(session.overall_quality_score)
        
        return {
            'calidad_promedio': np.mean(quality_scores) if quality_scores else 0,
            'calidad_minima': min(quality_scores) if quality_scores else 0,
            'calidad_maxima': max(quality_scores) if quality_scores else 0,
            'muestras_calidad_alta': sum(1 for s in quality_scores if s >= 0.8),
            'muestras_calidad_baja': sum(1 for s in quality_scores if s < 0.6)
        }
    
    def _create_statistical_summary(self, sessions_data: List[Any]) -> List[Dict]:
        """Crea resumen estadístico detallado"""
        summary = []
        
        for ptype in PINEAPPLE_CODES.keys():
            for mstate in MATURITY_STATES.keys():
                matching_sessions = [
                    session for session in sessions_data
                    if (getattr(session, 'pineapple_type', None) == ptype and
                        getattr(session, 'maturity_state', None) == mstate) or
                       (session.get('pineapple_type') == ptype and
                        session.get('maturity_state') == mstate)
                ]
                
                if matching_sessions:
                    group_r = []
                    group_g = []
                    group_b = []
                    
                    for session in matching_sessions:
                        rgb_data = self._extract_rgb_from_session(session)
                        group_r.extend(rgb_data['red'])
                        group_g.extend(rgb_data['green'])
                        group_b.extend(rgb_data['blue'])
                    
                    summary.append({
                        'Tipo_Piña': ptype,
                        'Estado_Madurez': mstate,
                        'Cantidad_Muestras': len(matching_sessions),
                        'Promedio_R': np.mean(group_r) if group_r else 0,
                        'Promedio_G': np.mean(group_g) if group_g else 0,
                        'Promedio_B': np.mean(group_b) if group_b else 0,
                        'StdDev_R': np.std(group_r) if group_r else 0,
                        'StdDev_G': np.std(group_g) if group_g else 0,
                        'StdDev_B': np.std(group_b) if group_b else 0
                    })
        
        return summary
    
    def _log_export(self, export_type: str, filepath: Path, session_count: int):
        """Registra exportación en log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': export_type,
            'filepath': str(filepath),
            'session_count': session_count,
            'file_size': filepath.stat().st_size if filepath.exists() else 0
        }
        
        self.export_log.append(log_entry)
    
    def get_export_history(self) -> List[Dict]:
        """Obtiene historial de exportaciones"""
        return self.export_log.copy()
    
    def cleanup_old_exports(self, days_old: int = 30):
        """Limpia exportaciones antiguas"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for folder in [self.excel_path, self.backup_path, self.reports_path]:
            for file_path in folder.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        st.info(f"🗑️ Archivo antiguo eliminado: {file_path.name}")
                    except Exception as e:
                        st.warning(f"⚠️ No se pudo eliminar {file_path.name}: {e}")

def export_single_session_simple(session_data: Any, filename: str = None) -> Optional[str]:
    """Función simplificada para exportar una sesión"""
    exporter = ChromabotExporter()
    return exporter.export_single_session(session_data, filename)

def export_multiple_sessions_simple(sessions_data: List[Any], filename: str = None) -> Optional[str]:
    """Función simplificada para exportar múltiples sesiones"""
    exporter = ChromabotExporter()
    return exporter.export_multiple_sessions(sessions_data, filename)

def create_ml_dataset(sessions_data: List[Any]) -> Optional[str]:
    """Crea dataset optimizado para ML"""
    exporter = ChromabotExporter()
    return exporter.export_dataset_for_ml(sessions_data)

def create_data_backup(sessions_data: List[Any], backup_name: str = None) -> Optional[str]:
    """Crea backup de datos"""
    exporter = ChromabotExporter()
    return exporter.create_backup(sessions_data, backup_name)