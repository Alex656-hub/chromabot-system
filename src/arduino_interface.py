import serial
import json
import time
import streamlit as st
from typing import Dict, List, Tuple, Optional

class ColorSensorInterface:
    """
    Interfaz para comunicación con sensor de color TCS3200 vía Arduino
    Proyecto 1: Recolección de Color
    """
    
    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: int = 5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.arduino = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Conecta con Arduino"""
        try:
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Esperar inicialización de Arduino
            
            # Verificar conexión
            self.send_command("GET_STATUS")
            response = self.read_response()
            
            if response and "ready" in response.get("status", ""):
                self.is_connected = True
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Error conectando Arduino: {e}")
            return False
    
    def disconnect(self):
        """Desconecta Arduino"""
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self.is_connected = False
    
    def send_command(self, command: str):
        """Envía comando a Arduino"""
        if self.arduino and self.arduino.is_open:
            self.arduino.write(f"{command}\n".encode())
            self.arduino.flush()
    
    def read_response(self, timeout: int = 10) -> Optional[Dict]:
        """Lee respuesta JSON desde Arduino"""
        if not self.arduino:
            return None
            
        start_time = time.time()
        buffer = ""
        
        while time.time() - start_time < timeout:
            if self.arduino.in_waiting > 0:
                data = self.arduino.readline().decode().strip()
                
                if data:
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        # Si no es JSON válido, continuar leyendo
                        buffer += data + "\n"
                        continue
            time.sleep(0.1)
        
        return None
    
    def capture_color_data(self) -> Optional[Dict]:
        """
        Captura 40 mediciones RGB y retorna los 20 datos centrales filtrados
        """
        if not self.is_connected:
            st.error("Arduino no conectado")
            return None
        
        try:
            # Iniciar captura
            self.send_command("START_CAPTURE")
            
            # Barra de progreso en Streamlit
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Leer respuestas durante la captura
            filtered_data = None
            
            while True:
                response = self.read_response(timeout=2)
                
                if not response:
                    continue
                
                # Actualizar progreso
                if "progress" in response:
                    progress = response["progress"]
                    progress_bar.progress(progress / 100)
                    status_text.text(f"Capturando... {progress}%")
                
                # Datos filtrados recibidos
                if "filtered_data" in response:
                    filtered_data = response["filtered_data"]
                
                # Captura completada
                if response.get("status") == "capture_complete":
                    progress_bar.progress(100)
                    status_text.text("✅ Captura completada")
                    break
            
            return filtered_data
            
        except Exception as e:
            st.error(f"Error durante captura: {e}")
            return None
    
    def get_single_reading(self) -> Optional[Dict]:
        """Obtiene una sola lectura RGB para testing"""
        if not self.is_connected:
            return None
        
        self.send_command("SINGLE_READ")
        response = self.read_response()
        
        if response and "single_reading" in response:
            return response["single_reading"]
        
        return None
    
    def calibrate_sensor(self) -> bool:
        """Calibra el sensor con referencia blanca"""
        if not self.is_connected:
            return False
        
        try:
            self.send_command("CALIBRATE")
            
            # Mostrar instrucciones de calibración
            st.info("🔧 Calibrando sensor...")
            st.warning("📋 Coloque una superficie blanca frente al sensor")
            
            # Esperar respuestas de calibración
            while True:
                response = self.read_response()
                
                if not response:
                    continue
                
                if "white_reference" in response:
                    white_ref = response["white_reference"]
                    st.success("✅ Calibración completada")
                    st.json(white_ref)
                    return True
                
                if response.get("calibration") == "complete":
                    break
            
            return True
            
        except Exception as e:
            st.error(f"Error en calibración: {e}")
            return False
    
    def test_connection(self) -> Dict:
        """Prueba la conexión y obtiene info del sensor"""
        if not self.is_connected:
            return {"status": "disconnected"}
        
        self.send_command("GET_STATUS")
        response = self.read_response()
        
        if response:
            return response
        else:
            return {"status": "no_response"}

# Función para uso en Streamlit
def initialize_color_sensor(port: str = "COM3") -> ColorSensorInterface:
    """
    Inicializa y conecta el sensor de color
    """
    sensor = ColorSensorInterface(port=port)
    
    if sensor.connect():
        st.success(f"✅ Sensor de color conectado en {port}")
        return sensor
    else:
        st.error(f"❌ No se pudo conectar al sensor en {port}")
        return None