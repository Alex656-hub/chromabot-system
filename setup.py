"""
Setup file para Chromabot System - Versión Profesional
Proyecto 1: Recolección de Color RGB para clasificación de madurez de piñas
Universidad Nacional Toribio Rodríguez de Mendoza
"""

from setuptools import setup, find_packages
import os
import sys

# Información del proyecto
PROJECT_NAME = "chromabot-system"
VERSION = "1.0.0"
DESCRIPTION = "Sistema de captura y análisis RGB para clasificación de madurez de piñas"
AUTHOR = "Jose Alex"
EMAIL = "7494911521@untrm.edu.pe"
URL = "https://github.com/Alex656-hub/chromabot-system.git"

# Leer README para descripción larga
def read_file(filename):
    """Lee un archivo y retorna su contenido"""
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return ""

# Leer requirements.txt para dependencias
def read_requirements(filename="requirements.txt"):
    """Lee requirements.txt y retorna lista de dependencias"""
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            requirements = []
            for line in fh:
                line = line.strip()
                # Ignorar comentarios y líneas vacías
                if line and not line.startswith("#"):
                    requirements.append(line)
            return requirements
    except FileNotFoundError:
        # Dependencias por defecto si no existe requirements.txt
        return [
            "streamlit>=1.28.0",
            "pandas>=1.5.0",
            "numpy>=1.21.0",
            "openpyxl>=3.0.0",
            "pyserial>=3.5",
            "matplotlib>=3.5.0",
            "plotly>=5.0.0",
            "scipy>=1.9.0",
        ]

# Verificar versión de Python
if sys.version_info < (3, 8):
    print("Error: Chromabot System requiere Python 3.8 o superior.")
    print(f"Tu versión actual es: {sys.version}")
    sys.exit(1)

# Descripción larga
long_description = read_file("README.md")
if not long_description:
    long_description = """
# Chromabot System - Proyecto 1: Recolección de Color

Sistema avanzado de captura y análisis de datos RGB para clasificación automática 
de madurez de piñas utilizando sensor TCS3200 y machine learning.

## Características Principales

- 🔬 Captura de datos RGB con sensor TCS3200
- 📊 Análisis estadístico avanzado y detección de outliers  
- 🎨 Conversión a espacios de color (RGB → HSV)
- 💾 Exportación profesional a Excel y datasets ML
- 🖥️ Interfaz web intuitiva con Streamlit
- 🤖 Preparación de datos para machine learning

## Instalación

```bash
pip install chromabot-system
```

## Uso

```bash
chromabot
# O alternativamente:
streamlit run app/main.py
```
"""

setup(
    # Información básica del proyecto
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Información del autor
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    
    # URLs del proyecto
    url=URL,
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Documentation": f"{URL}/docs",
        "Source Code": URL,
        "Funding": "https://untrm.edu.pe",
        "Say Thanks!": f"{URL}/stargazers",
    },
    
    # Configuración de paquetes
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    package_dir={"": "."},
    include_package_data=True,
    zip_safe=False,
    
    # Archivos adicionales a incluir
    package_data={
        "": ["*.md", "*.txt", "*.rst", "*.cfg", "*.ini"],
        "app": ["*.py", "*.json"],
        "src": ["*.py"],
        "arduino": ["*.ino", "*.cpp", "*.h"],
        "docs": ["*.md", "*.rst"],
        "data": [".gitkeep"],
    },
    
    # Datos adicionales fuera del paquete
    data_files=[
        ("", ["README.md", "requirements.txt"]),
        ("arduino", ["arduino/pineapple_sensors.ino", "arduino/test_simple.ino"]),
    ],
    
    # Requisitos del sistema
    python_requires=">=3.8",
    
    # Dependencias principales
    install_requires=read_requirements(),
    
    # Dependencias opcionales para diferentes usos
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.15.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-mock>=3.6.0",
            "coverage>=5.5.0",
        ],
        "hardware": [
            "pyserial>=3.5",
            "arduino-python3>=0.6",
        ],
        "ml": [
            "scikit-learn>=1.0.0",
            "xgboost>=1.5.0",
            "tensorflow>=2.8.0",
        ],
        "all": [
            "pytest>=6.0.0", "black>=22.0.0", "sphinx>=4.0.0",
            "scikit-learn>=1.0.0", "pyserial>=3.5",
        ]
    },
    
    # Scripts de línea de comandos
    entry_points={
        "console_scripts": [
            "chromabot=app.main:main",
            "chromabot-capture=src.data_capture:main",
            "chromabot-process=src.data_processing:main", 
            "chromabot-export=src.export_utils:main",
            "chromabot-arduino=src.arduino_interface:main",
        ],
    },
    
    # Metadatos para PyPI
    classifiers=[
        # Estado de desarrollo
        "Development Status :: 4 - Beta",
        
        # Audiencia objetivo
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        
        # Licencia
        "License :: OSI Approved :: MIT License",
        
        # Sistema operativo
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        
        # Versiones de Python soportadas
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Temas
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        
        # Lenguajes naturales
        "Natural Language :: Spanish",
        "Natural Language :: English",
        
        # Tipo de interfaz
        "Environment :: Web Environment",
        "Environment :: Console",
        
        # Framework específico
        "Framework :: Jupyter",
    ],
    
    # Palabras clave para búsqueda
    keywords=[
        "rgb", "color", "pineapple", "piña", "maturity", "madurez",
        "classification", "clasificacion", "machine-learning", "ml",
        "agriculture", "agricultura", "sensors", "sensores", "tcs3200",
        "streamlit", "data-analysis", "computer-vision", "iot",
    ],
    
    # Configuración adicional
    platforms=["any"],
    license="MIT",
    
    # Configuración de tests
    test_suite="tests",
    tests_require=["pytest>=6.0.0"],
    
    # Comandos personalizados de setup
    cmdclass={},
    
    # Configuración de namespace packages (si fuera necesario)
    # namespace_packages=[],
)