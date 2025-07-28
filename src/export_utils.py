"""
Chromabot System - Proyecto 1: Recolección de Color
Módulo de exportación de datos a Excel y otros formatos

Funcionalidades:
- Exportación a Excel con formato estándar
- Exportación masiva de múltiples sesiones
- Generación de reportes automáticos
- Backup y versionado de datos
- Validación de integridad de archivos
"""

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

# Determinar la ruta correcta del proyecto
def get_project_root() -> Path:
    """Encuentra la raíz del proyecto de manera confiable"""
    current_file = Path(__file__).resolve()
    
    # Buscar la raíz del proyecto (donde está requirements.txt o main.py)
    search_path = current_file.parent
    max_levels = 5  # Límite de seguridad
    
    for _ in range(max_levels):
        if (search_path / "requirements.txt").exists() or \
           (search_path / "main.py").exists() or \
           (search_path / "app").is_dir():
            return search_path
        
        parent = search_path.parent
        if parent == search_path:  # Llegamos a la raíz del sistema
            break
        search_path = parent
    
    # Fallback: usar directorio padre del archivo actual
    return current_file.parent.parent

# Configurar path del proyecto
PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT / "app"))

from app.config import (DATA_STRUCTURE, EXPORT_CONFIG, PINEAPPLE_CODES, 
                       MATURITY_STATES, COLOR_SENSOR_CONFIG)

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
        # Determinar la ruta correcta del proyecto
        self.project_root = get_project_root()
        
        if base_path is None:
            # Usar estructura estándar del proyecto
            data_root = self.project_root / "data"
        else:
            data_root = Path(base_path)
        
        # Crear directorio data si no existe
        data_root.mkdir(parents=True, exist_ok=True)
        
        # Rutas específicas - TODAS absolutas y relativas a la raíz del proyecto
        self.data_root = data_root
        self.excel_path = data_root / "exports"
        self.backup_path = data_root / "backups"
        self.reports_path = data_root / "reports" 
        self.samples_path = data_root / "samples"
        
        # Crear todos los directorios necesarios
        for path in [self.excel_path, self.backup_path, self.reports_path, self.samples_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.current_dataset = []
        self.export_log = []
        
        # Log de inicialización para debugging
        print(f"📁 ChromabotExporter inicializado:")
        print(f"   - Raíz proyecto: {self.project_root}")
        print(f"   - Datos raíz: {self.data_root}")  
        print(f"   - Excel: {self.excel_path}")
        print(f"   - Backups: {self.backup_path}")
        print(f"   - Reportes: {self.reports_path}")
        print(f"   - Muestras: {self.samples_path}")
    
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
            # Preparar datos para exportación
            export_data = self._prepare_session_data(session_data, include_raw_data)
            
            # Crear DataFrame
            df = pd.DataFrame([export_data])
            
            # Generar nombre de archivo
            if not filename:
                timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
                filename = f"{EXPORT_CONFIG['excel_filename']}_{timestamp}.xlsx"
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = self.excel_path / filename
            
            # Exportar con formato
            self._write_formatted_excel(df, filepath, single_session=True)
            
            # Registrar exportación
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
            
            # Preparar datos de todas las sesiones
            export_data_list = []
            for session in sessions_data:
                export_data = self._prepare_session_data(session, include_raw_data=True)
                export_data_list.append(export_data)
            
            # Crear DataFrame principal
            df_main = pd.DataFrame(export_data_list)
            
            # Generar nombre de archivo
            if not filename:
                timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
                count = len(sessions_data)
                filename = f"{EXPORT_CONFIG['excel_filename']}_dataset_{count}samples_{timestamp}.xlsx"
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = self.excel_path / filename
            
            # Exportar con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal con datos
                df_main.to_excel(writer, sheet_name=EXPORT_CONFIG["sheet_name"], 
                               index=False)
                
                # Hoja de resumen si se solicita
                if include_summary:
                    df_summary = self._create_summary_sheet(df_main)
                    df_summary.to_excel(writer, sheet_name="Resumen", index=False)
                
                # Hoja de metadatos
                df_metadata = self._create_metadata_sheet(sessions_data)
                df_metadata.to_excel(writer, sheet_name="Metadatos", index=False)
                
                # Aplicar formato
                self._apply_excel_formatting(writer, df_main)
            
            # Registrar exportación
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
                # Datos básicos
                basic_data = self._prepare_session_data(session, include_raw_data=False)
                
                # Features de ML si se solicita
                if include_features:
                    rgb_data = self._extract_rgb_from_session(session)
                    features = processor.extract_features(rgb_data)
                    basic_data.update(features)
                
                ml_data.append(basic_data)
            
            # Crear DataFrame
            df_ml = pd.DataFrame(ml_data)
            
            # Filename específico para ML
            timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
            filename = f"chromabot_ml_dataset_{len(sessions_data)}samples_{timestamp}.xlsx"
            filepath = self.excel_path / filename
            
            # Exportar con hojas especializadas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Dataset principal
                df_ml.to_excel(writer, sheet_name="ML_Dataset", index=False)
                
                # Diccionario de variables
                df_variables = self._create_variable_dictionary(df_ml)
                df_variables.to_excel(writer, sheet_name="Variables", index=False)
                
                # Estadísticas descriptivas
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
                # Exportar datos a Excel temporal
                temp_excel = self.export_multiple_sessions(sessions_data, 
                                                         f"temp_backup_{timestamp}")
                if temp_excel:
                    zipf.write(temp_excel, f"data_{timestamp}.xlsx")
                
                # Añadir datos raw en JSON
                json_data = self._sessions_to_json(sessions_data)
                json_file = self.backup_path / f"temp_data_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, default=str)
                zipf.write(json_file, f"raw_data_{timestamp}.json")
                
                # Añadir metadatos
                metadata = self._create_backup_metadata(sessions_data)
                metadata_file = self.backup_path / f"temp_metadata_{timestamp}.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, default=str)
                zipf.write(metadata_file, f"metadata_{timestamp}.json")
                
                # Limpiar archivos temporales
                for temp_file in [json_file, metadata_file]:
                    if temp_file.exists():
                        temp_file.unlink()
            
            # Calcular checksum
            checksum = self._calculate_file_checksum(backup_file)
            
            # Guardar info del backup
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
            
            # Crear DataFrame del reporte
            report_sections = []
            
            # Información general
            for key, value in report_data['general_info'].items():
                report_sections.append({
                    'Sección': 'Información General',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            # Distribución
            for key, value in report_data['distribution_analysis'].items():
                report_sections.append({
                    'Sección': 'Análisis de Distribución',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            # Calidad
            for key, value in report_data['quality_analysis'].items():
                report_sections.append({
                    'Sección': 'Análisis de Calidad',
                    'Parámetro': key,
                    'Valor': str(value)
                })
            
            df_report = pd.DataFrame(report_sections)
            
            # Generar archivo
            timestamp = datetime.now().strftime(EXPORT_CONFIG["date_format"])
            filename = f"chromabot_report_{timestamp}.xlsx"
            filepath = self.reports_path / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_report.to_excel(writer, sheet_name="Reporte", index=False)
                
                # Estadísticas detalladas
                df_stats = pd.DataFrame(report_data['statistical_summary'])
                df_stats.to_excel(writer, sheet_name="Estadisticas_Detalladas", index=False)
            
            st.success(f"✅ Reporte generado: {filename}")
            return str(filepath)
            
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            return None
    
    def _prepare_session_data(self, session_data: Any, 
                            include_raw_data: bool = True) -> Dict[str, Any]:
        """Prepara datos de sesión para exportación"""
        
        # Obtener datos básicos
        if hasattr(session_data, 'sample_id'):
            # Objeto CaptureSession
            basic_data = {
                'sample_id': session_data.sample_id,
                'pineapple_type': session_data.pineapple_type,
                'pineapple_code': session_data.pineapple_code,
                'maturity_state': session_data.maturity_state,
                'maturity_code': session_data.maturity_code,
                'timestamp': session_data.capture_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'measurement_notes': session_data.notes,
                'is_simulation': session_data.is_simulation
            }
            
            # Datos RGB
            if session_data.filtered_readings:
                r_values = [r.red for r in session_data.filtered_readings]
                g_values = [r.green for r in session_data.filtered_readings]
                b_values = [r.blue for r in session_data.filtered_readings]
            else:
                r_values = g_values = b_values = []
            
            # Promedios
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
            
        else:
            # Datos directos (diccionario)
            basic_data = {
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
                'is_simulation': session_data.get('is_simulation', False)
            }
            
            r_values = session_data.get('r_values', [])
            g_values = session_data.get('g_values', [])
            b_values = session_data.get('b_values', [])
        
        # Añadir datos raw si se solicita
        if include_raw_data:
            basic_data.update({
                'r_values': str(r_values),  # Convertir a string para Excel
                'g_values': str(g_values),
                'b_values': str(b_values),
                'total_readings': len(r_values)
            })
        
        return basic_data
    
    def _extract_rgb_from_session(self, session_data: Any) -> Dict[str, List[int]]:
        """Extrae valores RGB de una sesión"""
        if hasattr(session_data, 'filtered_readings'):
            # Objeto CaptureSession
            return {
                'red': [r.red for r in session_data.filtered_readings],
                'green': [r.green for r in session_data.filtered_readings],
                'blue': [r.blue for r in session_data.filtered_readings]
            }
        else:
            # Datos directos
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
            
            # Formato de cabeceras
            header_format = workbook.create_style(
                font=workbook.create_font(bold=True, color='FFFFFF'),
                fill=workbook.create_fill(fill_type='solid', start_color='4472C4')
            )
            
            # Aplicar formato a cabeceras
            for col in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col)
                cell.style = header_format
            
            # Ajustar ancho de columnas
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
            
            # Formato alternado de filas
            for row in range(2, len(df) + 2):
                if row % 2 == 0:
                    for col in range(1, len(df.columns) + 1):
                        cell = worksheet.cell(row=row, column=col)
                        cell.fill = workbook.create_fill(
                            fill_type='solid', start_color='F8F9FA'
                        )
    
    def _create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea hoja de resumen estadístico"""
        summary_data = []
        
        # Conteos por tipo de piña
        pineapple_counts = df['pineapple_type'].value_counts()
        for ptype, count in pineapple_counts.items():
            summary_data.append({
                'Categoría': 'Tipo de Piña',
                'Valor': ptype,
                'Cantidad': count,
                'Porcentaje': f"{(count/len(df)*100):.1f}%"
            })
        
        # Conteos por estado de madurez
        maturity_counts = df['maturity_state'].value_counts()
        for mstate, count in maturity_counts.items():
            summary_data.append({
                'Categoría': 'Estado Madurez',
                'Valor': mstate,
                'Cantidad': count,
                'Porcentaje': f"{(count/len(df)*100):.1f}%"
            })
        
        # Estadísticas RGB
        for channel in ['r_avg', 'g_avg', 'b_avg']:
            if channel in df.columns:
                channel_name = channel.replace('_avg', '').upper()
                summary_data.append({
                    'Categoría': f'Promedio {channel_name}',
                    'Valor': 'Media',
                    'Cantidad': f"{df[channel].mean():.1f}",
                    'Porcentaje': f"±{df[channel].std():.1f}"
                })
        
        return pd.DataFrame(summary_data)
    
    def _create_metadata_sheet(self, sessions_data: List[Any]) -> pd.DataFrame:
        """Crea hoja de metadatos del experimento"""
        metadata = []
        
        # Información del sistema
        metadata.extend([
            {'Parámetro': 'Proyecto', 'Valor': 'Chromabot - Recolección de Color'},
            {'Parámetro': 'Sensor', 'Valor': COLOR_SENSOR_CONFIG['model']},
            {'Parámetro': 'Fecha Exportación', 'Valor': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {'Parámetro': 'Total Muestras', 'Valor': str(len(sessions_data))},
            {'Parámetro': 'Datos por Muestra', 'Valor': str(COLOR_SENSOR_CONFIG.get('data_points_per_sample', 'N/A'))},
            {'Parámetro': 'Canales RGB', 'Valor': ', '.join(COLOR_SENSOR_CONFIG['channels'])}
        ])
        
        # Códigos de clasificación
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
            'r_avg': 'Promedio canal Rojo (0-4000)',
            'g_avg': 'Promedio canal Verde (0-4000)',
            'b_avg': 'Promedio canal Azul (0-4000)',
            'timestamp': 'Fecha y hora de captura',
            'red_mean': 'Media estadística canal Rojo',
            'red_std': 'Desviación estándar canal Rojo',
            'hue_mean': 'Matiz promedio (0-360°)',
            'saturation_mean': 'Saturación promedio (0-1)',
            'color_temperature': 'Temperatura de color estimada (K)'
        }
        
        return descriptions.get(column, f'Variable {column}')
    
    def _create_descriptive_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea estadísticas descriptivas"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        stats_df = df[numeric_columns].describe()
        
        # Transponer para mejor lectura
        stats_df = stats_df.transpose()
        stats_df.reset_index(inplace=True)
        stats_df.rename(columns={'index': 'Variable'}, inplace=True)
        
        return stats_df
    
    def _sessions_to_json(self, sessions_data: List[Any]) -> List[Dict]:
        """Convierte sesiones a formato JSON"""
        json_data = []
        
        for session in sessions_data:
            if hasattr(session, 'sample_id'):
                # Objeto CaptureSession
                session_dict = {
                    'sample_id': session.sample_id,
                    'pineapple_type': session.pineapple_type,
                    'pineapple_code': session.pineapple_code,
                    'maturity_state': session.maturity_state,
                    'maturity_code': session.maturity_code,
                    'capture_timestamp': session.capture_timestamp.isoformat(),
                    'notes': session.notes,
                    'is_simulation': session.is_simulation,
                    'averages': session.averages,
                    'statistics': session.statistics,
                    'filtered_readings': [
                        {
                            'red': r.red,
                            'green': r.green,
                            'blue': r.blue,
                            'timestamp': r.timestamp.isoformat(),
                            'quality_score': r.quality_score
                        } for r in session.filtered_readings
                    ]
                }
            else:
                # Datos directos
                session_dict = dict(session)
            
            json_data.append(session_dict)
        
        return json_data
    
    def _create_backup_metadata(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Crea metadatos para backup"""
        return {
            'backup_info': {
                'created': datetime.now().isoformat(),
                'chromabot_version': '1.0',
                'project': 'Recolección de Color',
                'total_sessions': len(sessions_data)
            },
            'data_structure': DATA_STRUCTURE,
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
        
        # Conteos por tipo
        type_counts = {}
        maturity_counts = {}
        simulation_count = 0
        
        for session in sessions_data:
            if hasattr(session, 'pineapple_type'):
                ptype = session.pineapple_type
                mstate = session.maturity_state
                is_sim = session.is_simulation
            else:
                ptype = session.get('pineapple_type', 'Unknown')
                mstate = session.get('maturity_state', 'Unknown')
                is_sim = session.get('is_simulation', False)
            
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
            maturity_counts[mstate] = maturity_counts.get(mstate, 0) + 1
            if is_sim:
                simulation_count += 1
        
        return {
            'total_muestras': total_sessions,
            'tipos_piña': type_counts,
            'estados_madurez': maturity_counts,
            'datos_simulados': simulation_count,
            'datos_reales': total_sessions - simulation_count
        }
    
    def _analyze_distribution(self, sessions_data: List[Any]) -> Dict[str, Any]:
        """Análisis de distribución del dataset"""
        # Extraer valores RGB
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
        from data_processing import RGBDataProcessor
        
        processor = RGBDataProcessor()
        quality_scores = []
        
        for session in sessions_data:
            rgb_data = self._extract_rgb_from_session(session)
            outliers = processor._detect_outliers(rgb_data)
            quality_metrics = processor._calculate_quality_metrics(rgb_data, outliers)
            
            overall_score = quality_metrics.get('overall', {}).get('quality_score', 0)
            quality_scores.append(overall_score)
        
        return {
            'calidad_promedio': np.mean(quality_scores) if quality_scores else 0,
            'calidad_minima': min(quality_scores) if quality_scores else 0,
            'calidad_maxima': max(quality_scores) if quality_scores else 0,
            'muestras_calidad_alta': sum(1 for s in quality_scores if s >= 80),
            'muestras_calidad_baja': sum(1 for s in quality_scores if s < 60)
        }
    
    def _create_statistical_summary(self, sessions_data: List[Any]) -> List[Dict]:
        """Crea resumen estadístico detallado"""
        summary = []
        
        # Agrupar por tipo y estado
        for ptype in PINEAPPLE_CODES.keys():
            for mstate in MATURITY_STATES.keys():
                # Filtrar sesiones que coincidan
                matching_sessions = [
                    session for session in sessions_data
                    if (getattr(session, 'pineapple_type', None) == ptype and
                        getattr(session, 'maturity_state', None) == mstate) or
                       (session.get('pineapple_type') == ptype and
                        session.get('maturity_state') == mstate)
                ]
                
                if matching_sessions:
                    # Calcular estadísticas RGB para este grupo
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

# Funciones de utilidad para uso en Streamlit
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