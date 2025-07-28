# 📚 Manual de Usuario - Chromabot System v1.0

## 🎯 Descripción General
Sistema de captura y análisis de datos RGB para clasificación de madurez de piñas usando sensor TCS3200.

## 🔧 Instalación

### Requisitos del Sistema
- Python 3.8 o superior
- Arduino IDE
- Windows/Linux/Mac
- Puerto USB libre

### Instalación Software
```bash
# 1. Clonar repositorio
git clone [URL_DEL_REPOSITORIO]
cd chromabot-system

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar paquete
pip install -e .

# 4. Ejecutar aplicación
cd app
streamlit run main.py
```

## ⚡ Configuración Hardware

### Conexiones TCS3200
```
Arduino Uno → TCS3200
VCC → 5V
GND → GND
S0 → Pin 4
S1 → Pin 5
S2 → Pin 6
S3 → Pin 7
OUT → Pin 8
```

### Configuración Arduino
1. Abrir Arduino IDE
2. Cargar archivo: `arduino/pineapple_sensors.ino`
3. Seleccionar puerto COM correcto
4. Subir código al Arduino

## 🚀 Uso del Sistema

### Proceso de Captura
1. **Conectar Hardware**
   - Arduino vía USB
   - Verificar puerto COM
   - Click "🔌 Conectar Arduino"

2. **Seleccionar Tipo de Piña**
   - Golden (MD-2): Código 1
   - Roja Española: Código 2  
   - Cayena: Código 3

3. **Seleccionar Estado de Madurez**
   - Verde: Código 1
   - Madura: Código 2
   - Sobre Madurada: Código 3

4. **Realizar Captura**
   - Posicionar piña frente al sensor
   - Click "🚀 Iniciar Captura de Color"
   - Esperar 40 mediciones → filtrado a 20

5. **Revisar Resultados**
   - Estadísticas RGB
   - Gráficos de calidad
   - Score de confiabilidad

6. **Exportar Datos**
   - Excel individual: "📁 Exportar Esta Sesión"
   - Dataset completo: "📊 Exportar Todas"
   - ML ready: "🤖 Dataset para ML"

## 📊 Interpretación de Resultados

### Estadísticas RGB
- **Media**: Valor promedio del canal
- **Desv. Std**: Variabilidad de mediciones
- **Min/Max**: Rango de valores capturados

### Score de Calidad (0-100)
- **90-100**: Excelente calidad
- **80-89**: Buena calidad
- **70-79**: Aceptable
- **<70**: Repetir captura

### Análisis Colorimétrico
- **Color Dominante**: Canal RGB más fuerte
- **Temperatura**: Estimación en Kelvin
- **Pureza**: Saturación del color (0-1)
- **Brillo**: Intensidad luminosa (0-1)

## 🔍 Troubleshooting

### "Arduino no conectado"
- Verificar cable USB
- Comprobar puerto COM en Device Manager
- Reinstalar drivers Arduino

### "Error en captura"
- Revisar conexiones TCS3200
- Verificar código Arduino cargado
- Calibrar sensor con superficie blanca

### "Módulos no disponibles"
- Ejecutar: `pip install -e .`
- Verificar estructura de carpetas
- Reinstalar dependencias

### "Datos de baja calidad"
- Mejorar iluminación (estable, difusa)
- Limpiar sensor TCS3200
- Posicionar piña más cerca del sensor
- Evitar sombras y reflejos

## ⚙️ Mantenimiento

### Calibración Regular
- Ejecutar con superficie blanca cada 10 capturas
- Limpiar sensor con aire comprimido
- Verificar conexiones periódicamente

### Backup de Datos
- Usar "💾 Crear Backup" en la interfaz
- Archivos se guardan en `data/backups/`
- Formato ZIP con checksums de integridad

## 📁 Estructura de Archivos
```
chromabot-system/
├── app/main.py          # Aplicación principal
├── src/                 # Módulos core
├── arduino/             # Código para Arduino
├── data/
│   ├── exports/         # Archivos Excel
│   ├── samples/         # Muestras procesadas
│   └── backups/         # Respaldos seguros
└── docs/               # Documentación
```

## 📞 Soporte
Para problemas técnicos:
1. Revisar este manual
2. Verificar logs en terminal
3. Contactar al desarrollador
4. GitHub Issues: [URL_REPOSITORIO]/issues

---
**Chromabot System v1.0** - Universidad Nacional Toribio Rodríguez de Mendoza