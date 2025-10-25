"""
Chromabot System - Proyecto 1: Recolección de Color
Módulo de procesamiento y análisis de datos RGB

Funcionalidades:
- Filtrado avanzado de datos
- Cálculo de estadísticas RGB
- Detección de outliers
- Análisis de calidad de datos
- Normalización y transformaciones
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import colorsys
from scipy import stats
from scipy.signal import savgol_filter
import logging

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.config import COLOR_SENSOR_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class RGBStatistics:
    """Estadísticas completas para un canal RGB"""
    mean: float
    median: float
    std: float
    variance: float
    min_val: int
    max_val: int
    q25: float
    q75: float
    iqr: float
    skewness: float
    kurtosis: float

@dataclass
class ColorAnalysis:
    """Análisis colorimétrico completo"""
    rgb_stats: Dict[str, RGBStatistics]
    hsv_values: Dict[str, List[float]]
    hsv_stats: Dict[str, RGBStatistics]
    color_temperature: float
    dominant_color: str
    color_purity: float
    brightness: float
    saturation: float

class RGBDataProcessor:
    """
    Procesador principal de datos RGB para análisis avanzado
    """
    
    def __init__(self):
        self.outlier_methods = ['iqr', 'zscore', 'modified_zscore']
        self.smoothing_methods = ['savgol', 'moving_average', 'gaussian']
        
    def process_rgb_session(self, session_data: Any) -> Dict[str, Any]:
        """
        Procesa una sesión completa de captura RGB
        
        Args:
            session_data: Objeto CaptureSession con datos RGB
            
        Returns:
            Dict con análisis completo procesado
        """
        try:
            # Extraer valores RGB
            rgb_data = self._extract_rgb_values(session_data)
            
            # Análisis estadístico básico
            rgb_stats = self._calculate_rgb_statistics(rgb_data)
            
            # Conversión a otros espacios de color
            hsv_data = self._convert_to_hsv(rgb_data)
            hsv_stats = self._calculate_rgb_statistics(hsv_data)
            
            # Análisis colorimétrico
            color_analysis = self._analyze_color_properties(rgb_data, hsv_data)
            
            # Detección de outliers
            outliers = self._detect_outliers(rgb_data)
            
            # Análisis de calidad
            quality_metrics = self._calculate_quality_metrics(rgb_data, outliers)
            
            # Análisis de tendencias
            trend_analysis = self._analyze_trends(rgb_data)
            
            return {
                'session_id': session_data.sample_id,
                'rgb_statistics': rgb_stats,
                'hsv_statistics': hsv_stats,
                'color_analysis': color_analysis,
                'outliers': outliers,
                'quality_metrics': quality_metrics,
                'trend_analysis': trend_analysis,
                'processed_timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            logger.exception("Error procesando sesión")
            return {}
    
    def _extract_rgb_values(self, session_data: Any) -> Dict[str, List[int]]:
        """Extrae valores RGB de la sesión"""
        if hasattr(session_data, 'filtered_readings'):
            # Datos de sesión completa
            red_vals = [r.red for r in session_data.filtered_readings]
            green_vals = [r.green for r in session_data.filtered_readings]
            blue_vals = [r.blue for r in session_data.filtered_readings]
        else:
            # Datos directos
            red_vals = session_data.get('r_values', [])
            green_vals = session_data.get('g_values', [])
            blue_vals = session_data.get('b_values', [])
        
        return {
            'red': red_vals,
            'green': green_vals,
            'blue': blue_vals
        }
    
    def _calculate_rgb_statistics(self, rgb_data: Dict[str, List]) -> Dict[str, RGBStatistics]:
        """Calcula estadísticas completas para cada canal RGB"""
        stats_dict = {}
        
        for channel, values in rgb_data.items():
            if not values:
                continue
                
            values_array = np.array(values)
            
            stats_dict[channel] = RGBStatistics(
                mean=float(np.mean(values_array)),
                median=float(np.median(values_array)),
                std=float(np.std(values_array)),
                variance=float(np.var(values_array)),
                min_val=int(np.min(values_array)),
                max_val=int(np.max(values_array)),
                q25=float(np.percentile(values_array, 25)),
                q75=float(np.percentile(values_array, 75)),
                iqr=float(np.percentile(values_array, 75) - np.percentile(values_array, 25)),
                skewness=float(stats.skew(values_array)),
                kurtosis=float(stats.kurtosis(values_array))
            )
        
        return stats_dict
    
    def _convert_to_hsv(self, rgb_data: Dict[str, List[int]]) -> Dict[str, List[float]]:
        """Convierte valores RGB a HSV"""
        red_vals = rgb_data['red']
        green_vals = rgb_data['green']
        blue_vals = rgb_data['blue']
        
        hsv_data = {'hue': [], 'saturation': [], 'value': []}
        
        for r, g, b in zip(red_vals, green_vals, blue_vals):
            # Normalizar RGB a 0-1
            r_norm = r / 255.0 if r <= 255 else r / 4000.0  # TCS3200 puede dar valores >255
            g_norm = g / 255.0 if g <= 255 else g / 4000.0
            b_norm = b / 255.0 if b <= 255 else b / 4000.0
            
            # Convertir a HSV
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            hsv_data['hue'].append(h * 360)      # Hue en grados (0-360)
            hsv_data['saturation'].append(s)    # Saturación (0-1)
            hsv_data['value'].append(v)         # Valor/Brillo (0-1)
        
        return hsv_data
    
    def _analyze_color_properties(self, rgb_data: Dict, hsv_data: Dict) -> Dict[str, Any]:
        """Analiza propiedades colorimétricas avanzadas"""
        
        # Calcular color dominante
        dominant_color = self._determine_dominant_color(rgb_data)
        
        # Temperatura de color estimada
        color_temp = self._estimate_color_temperature(rgb_data)
        
        # Pureza del color (basada en saturación)
        color_purity = np.mean(hsv_data['saturation'])
        
        # Brillo promedio
        brightness = np.mean(hsv_data['value'])
        
        # Análisis de distribución de matiz
        hue_distribution = self._analyze_hue_distribution(hsv_data['hue'])
        
        return {
            'dominant_color': dominant_color,
            'color_temperature': color_temp,
            'color_purity': color_purity,
            'brightness': brightness,
            'hue_distribution': hue_distribution
        }
    
    def _determine_dominant_color(self, rgb_data: Dict) -> str:
        """Determina el color dominante basado en promedios RGB"""
        avg_red = np.mean(rgb_data['red'])
        avg_green = np.mean(rgb_data['green'])
        avg_blue = np.mean(rgb_data['blue'])
        
        max_channel = max(avg_red, avg_green, avg_blue)
        
        if max_channel == avg_red:
            if avg_red > avg_green * 1.2 and avg_red > avg_blue * 1.2:
                return "Rojo"
            elif avg_green > avg_blue * 1.2:
                return "Amarillo"
            else:
                return "Magenta"
        elif max_channel == avg_green:
            if avg_green > avg_red * 1.2 and avg_green > avg_blue * 1.2:
                return "Verde"
            elif avg_red > avg_blue * 1.2:
                return "Amarillo"
            else:
                return "Cian"
        else:  # max_channel == avg_blue
            if avg_blue > avg_red * 1.2 and avg_blue > avg_green * 1.2:
                return "Azul"
            elif avg_red > avg_green * 1.2:
                return "Magenta"
            else:
                return "Cian"
    
    def _estimate_color_temperature(self, rgb_data: Dict) -> float:
        """Estima temperatura de color en Kelvin (aproximación)"""
        avg_red = np.mean(rgb_data['red'])
        avg_green = np.mean(rgb_data['green'])
        avg_blue = np.mean(rgb_data['blue'])
        
        # Normalizar
        total = avg_red + avg_green + avg_blue
        if total == 0:
            return 6500  # Luz día por defecto
        
        r_norm = avg_red / total
        g_norm = avg_green / total
        b_norm = avg_blue / total
        
        # Aproximación simple basada en balance RGB
        if r_norm > b_norm:
            # Más cálido (más rojo que azul)
            temp = 2000 + (b_norm / r_norm) * 4500
        else:
            # Más frío (más azul que rojo)
            temp = 6500 + (b_norm - r_norm) * 3500
        
        return max(2000, min(10000, temp))  # Limitar rango
    
    def _analyze_hue_distribution(self, hue_values: List[float]) -> Dict[str, Any]:
        """Analiza la distribución de matices"""
        hue_array = np.array(hue_values)
        
        # Dividir el círculo cromático en segmentos
        segments = {
            'Rojo': (0, 30),
            'Naranja': (30, 60),
            'Amarillo': (60, 120),
            'Verde': (120, 180),
            'Cian': (180, 240),
            'Azul': (240, 300),
            'Magenta': (300, 360)
        }
        
        distribution = {}
        for color, (start, end) in segments.items():
            count = np.sum((hue_array >= start) & (hue_array < end))
            distribution[color] = count / len(hue_values) if len(hue_values) > 0 else 0
        
        return distribution
    
    def _detect_outliers(self, rgb_data: Dict) -> Dict[str, Dict]:
        """Detecta outliers en datos RGB usando múltiples métodos"""
        outliers = {}
        
        for channel, values in rgb_data.items():
            if not values:
                continue
                
            values_array = np.array(values)
            channel_outliers = {}
            
            # Método IQR
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            iqr_outliers = np.where((values_array < lower_bound) | (values_array > upper_bound))[0]
            channel_outliers['iqr'] = {
                'indices': iqr_outliers.tolist(),
                'values': values_array[iqr_outliers].tolist(),
                'bounds': {'lower': lower_bound, 'upper': upper_bound}
            }
            
            # Método Z-Score
            z_scores = np.abs(stats.zscore(values_array))
            zscore_outliers = np.where(z_scores > 2.5)[0]
            channel_outliers['zscore'] = {
                'indices': zscore_outliers.tolist(),
                'values': values_array[zscore_outliers].tolist(),
                'threshold': 2.5
            }
            
            # Método Z-Score Modificado (MAD)
            median = np.median(values_array)
            mad = np.median(np.abs(values_array - median))
            modified_z_scores = 0.6745 * (values_array - median) / mad if mad != 0 else np.zeros_like(values_array)
            mad_outliers = np.where(np.abs(modified_z_scores) > 3.5)[0]
            channel_outliers['modified_zscore'] = {
                'indices': mad_outliers.tolist(),
                'values': values_array[mad_outliers].tolist(),
                'threshold': 3.5
            }
            
            outliers[channel] = channel_outliers
        
        return outliers
    
    def _calculate_quality_metrics(self, rgb_data: Dict, outliers: Dict) -> Dict[str, Any]:
        """Calcula métricas de calidad de los datos"""
        quality_metrics = {}
        
        for channel, values in rgb_data.items():
            if not values:
                continue
            
            values_array = np.array(values)
            channel_outliers = outliers.get(channel, {})
            
            # Conteo de outliers por método
            outlier_counts = {method: len(data['indices']) 
                            for method, data in channel_outliers.items()}
            
            # Porcentaje de outliers
            total_outliers = len(set().union(*[data['indices'] for data in channel_outliers.values()]))
            outlier_percentage = (total_outliers / len(values)) * 100 if len(values) > 0 else 0
            
            # Coeficiente de variación
            cv = (np.std(values_array) / np.mean(values_array)) * 100 if np.mean(values_array) != 0 else 0
            
            # Estabilidad (diferencia entre primera y última mitad)
            mid_point = len(values) // 2
            first_half_mean = np.mean(values_array[:mid_point])
            second_half_mean = np.mean(values_array[mid_point:])
            stability = abs(first_half_mean - second_half_mean) / max(first_half_mean, second_half_mean) * 100
            
            # Score de calidad general (0-100)
            quality_score = 100
            quality_score -= min(outlier_percentage * 2, 30)  # Penalizar outliers
            quality_score -= min(cv, 20)  # Penalizar alta variabilidad
            quality_score -= min(stability, 15)  # Penalizar inestabilidad
            quality_score = max(0, quality_score)
            
            quality_metrics[channel] = {
                'outlier_counts': outlier_counts,
                'outlier_percentage': outlier_percentage,
                'coefficient_variation': cv,
                'stability': stability,
                'quality_score': quality_score
            }
        
        # Score general promedio
        overall_score = np.mean([metrics['quality_score'] for metrics in quality_metrics.values()])
        quality_metrics['overall'] = {
            'quality_score': overall_score,
            'classification': self._classify_quality(overall_score)
        }
        
        return quality_metrics
    
    def _classify_quality(self, score: float) -> str:
        """Clasifica la calidad basada en el score"""
        if score >= 90:
            return "Excelente"
        elif score >= 80:
            return "Buena"
        elif score >= 70:
            return "Aceptable"
        elif score >= 60:
            return "Regular"
        else:
            return "Deficiente"
    
    def _analyze_trends(self, rgb_data: Dict) -> Dict[str, Any]:
        """Analiza tendencias temporales en los datos"""
        trends = {}
        
        for channel, values in rgb_data.items():
            if not values or len(values) < 5:
                continue
            
            values_array = np.array(values)
            x = np.arange(len(values_array))
            
            # Regresión lineal para tendencia
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values_array)
            
            # Dirección de tendencia
            if abs(slope) < 1:
                trend_direction = "Estable"
            elif slope > 0:
                trend_direction = "Creciente"
            else:
                trend_direction = "Decreciente"
            
            # Suavizado para detectar patrones
            if len(values_array) >= 5:
                smoothed = savgol_filter(values_array, min(5, len(values_array)//2*2+1), 2)
                smoothing_difference = np.mean(np.abs(values_array - smoothed))
            else:
                smoothed = values_array
                smoothing_difference = 0
            
            trends[channel] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value,
                'trend_direction': trend_direction,
                'trend_strength': abs(slope),
                'smoothing_difference': smoothing_difference,
                'is_significant': p_value < 0.05
            }
        
        return trends
    
    def apply_smoothing(self, rgb_data: Dict, method: str = 'savgol', **kwargs) -> Dict[str, List[float]]:
        """Aplica suavizado a los datos RGB"""
        smoothed_data = {}
        
        for channel, values in rgb_data.items():
            if not values or len(values) < 5:
                smoothed_data[channel] = values
                continue
            
            values_array = np.array(values, dtype=float)
            
            if method == 'savgol':
                window_length = kwargs.get('window_length', min(5, len(values_array)//2*2+1))
                polyorder = kwargs.get('polyorder', 2)
                smoothed = savgol_filter(values_array, window_length, polyorder)
            
            elif method == 'moving_average':
                window = kwargs.get('window', 3)
                smoothed = np.convolve(values_array, np.ones(window)/window, mode='same')
            
            elif method == 'gaussian':
                sigma = kwargs.get('sigma', 1.0)
                from scipy.ndimage import gaussian_filter1d
                smoothed = gaussian_filter1d(values_array, sigma)
            
            else:
                smoothed = values_array
            
            smoothed_data[channel] = smoothed.tolist()
        
        return smoothed_data
    
    def normalize_rgb_data(self, rgb_data: Dict, method: str = 'minmax') -> Dict[str, List[float]]:
        """Normaliza datos RGB usando diferentes métodos"""
        normalized_data = {}
        
        for channel, values in rgb_data.items():
            if not values:
                normalized_data[channel] = values
                continue
            
            values_array = np.array(values, dtype=float)
            
            if method == 'minmax':
                # Normalización Min-Max (0-1)
                min_val = np.min(values_array)
                max_val = np.max(values_array)
                if max_val != min_val:
                    normalized = (values_array - min_val) / (max_val - min_val)
                else:
                    normalized = np.zeros_like(values_array)
            
            elif method == 'zscore':
                # Normalización Z-score (media=0, std=1)
                mean_val = np.mean(values_array)
                std_val = np.std(values_array)
                if std_val != 0:
                    normalized = (values_array - mean_val) / std_val
                else:
                    normalized = np.zeros_like(values_array)
            
            elif method == 'robust':
                # Normalización robusta usando mediana y MAD
                median_val = np.median(values_array)
                mad = np.median(np.abs(values_array - median_val))
                if mad != 0:
                    normalized = (values_array - median_val) / mad
                else:
                    normalized = np.zeros_like(values_array)
            
            else:
                normalized = values_array
            
            normalized_data[channel] = normalized.tolist()
        
        return normalized_data
    
    def extract_features(self, rgb_data: Dict) -> Dict[str, float]:
        """Extrae características relevantes para machine learning"""
        features = {}
        
        # Procesar datos
        rgb_stats = self._calculate_rgb_statistics(rgb_data)
        hsv_data = self._convert_to_hsv(rgb_data)
        hsv_stats = self._calculate_rgb_statistics(hsv_data)
        
        # Features estadísticas RGB
        for channel in ['red', 'green', 'blue']:
            if channel in rgb_stats:
                stats_obj = rgb_stats[channel]
                features[f'{channel}_mean'] = stats_obj.mean
                features[f'{channel}_std'] = stats_obj.std
                features[f'{channel}_median'] = stats_obj.median
                features[f'{channel}_iqr'] = stats_obj.iqr
                features[f'{channel}_skewness'] = stats_obj.skewness
                features[f'{channel}_kurtosis'] = stats_obj.kurtosis
        
        # Features HSV
        hsv_channels = ['hue', 'saturation', 'value']
        for i, channel in enumerate(hsv_channels):
            if channel in hsv_stats:
                stats_obj = hsv_stats[channel]
                features[f'{channel}_mean'] = stats_obj.mean
                features[f'{channel}_std'] = stats_obj.std
        
        # Features de ratios RGB
        if all(ch in rgb_stats for ch in ['red', 'green', 'blue']):
            r_mean = rgb_stats['red'].mean
            g_mean = rgb_stats['green'].mean
            b_mean = rgb_stats['blue'].mean
            
            total = r_mean + g_mean + b_mean
            if total > 0:
                features['r_ratio'] = r_mean / total
                features['g_ratio'] = g_mean / total
                features['b_ratio'] = b_mean / total
                features['rg_ratio'] = r_mean / g_mean if g_mean > 0 else 0
                features['rb_ratio'] = r_mean / b_mean if b_mean > 0 else 0
                features['gb_ratio'] = g_mean / b_mean if b_mean > 0 else 0
        
        # Features de color
        color_analysis = self._analyze_color_properties(rgb_data, hsv_data)
        features['color_temperature'] = color_analysis['color_temperature']
        features['color_purity'] = color_analysis['color_purity']
        features['brightness'] = color_analysis['brightness']
        
        return features
    
    def compare_sessions(self, session1: Dict, session2: Dict) -> Dict[str, Any]:
        """Compara dos sesiones de captura RGB"""
        comparison = {}
        
        # Extraer features de ambas sesiones
        features1 = self.extract_features(self._extract_rgb_values(session1))
        features2 = self.extract_features(self._extract_rgb_values(session2))
        
        # Calcular diferencias
        differences = {}
        for feature in features1.keys():
            if feature in features2:
                diff = abs(features1[feature] - features2[feature])
                rel_diff = diff / max(abs(features1[feature]), abs(features2[feature]), 1e-10) * 100
                differences[feature] = {
                    'absolute_diff': diff,
                    'relative_diff': rel_diff,
                    'session1_value': features1[feature],
                    'session2_value': features2[feature]
                }
        
        # Calcular similitud general
        similarity_scores = [100 - min(100, diff['relative_diff']) for diff in differences.values()]
        overall_similarity = np.mean(similarity_scores) if similarity_scores else 0
        
        comparison = {
            'session1_id': getattr(session1, 'sample_id', 'Unknown'),
            'session2_id': getattr(session2, 'sample_id', 'Unknown'),
            'feature_differences': differences,
            'overall_similarity': overall_similarity,
            'similarity_classification': self._classify_similarity(overall_similarity)
        }
        
        return comparison
    
    def _classify_similarity(self, similarity: float) -> str:
        """Clasifica el nivel de similitud"""
        if similarity >= 95:
            return "Prácticamente idénticas"
        elif similarity >= 85:
            return "Muy similares"
        elif similarity >= 70:
            return "Similares"
        elif similarity >= 50:
            return "Moderadamente diferentes"
        else:
            return "Muy diferentes"

# Funciones de utilidad para uso en Streamlit
def process_capture_session(session_data: Any) -> Dict[str, Any]:
    """Función simplificada para procesar una sesión"""
    processor = RGBDataProcessor()
    return processor.process_rgb_session(session_data)

def extract_ml_features(rgb_data: Dict) -> Dict[str, float]:
    """Extrae features para machine learning"""
    processor = RGBDataProcessor()
    return processor.extract_features(rgb_data)

def detect_data_outliers(rgb_data: Dict) -> Dict[str, Dict]:
    """Detecta outliers en datos RGB"""
    processor = RGBDataProcessor()
    return processor._detect_outliers(rgb_data)

def calculate_data_quality(rgb_data: Dict) -> Dict[str, Any]:
    """Calcula métricas de calidad"""
    processor = RGBDataProcessor()
    outliers = processor._detect_outliers(rgb_data)
    return processor._calculate_quality_metrics(rgb_data, outliers)