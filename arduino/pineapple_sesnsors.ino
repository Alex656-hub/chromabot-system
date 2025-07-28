/*
  Chromabot System - Proyecto 1: Recolección de Color
  Sensor TCS3200 optimizado para captura de datos RGB de piñas
  Captura 40 mediciones y envía las 20 centrales filtradas
  
  Comunicación bidireccional con Python/Streamlit
  Autor: Chromabot Team
*/

#define S0 4          // S0 a pin 4
#define S1 5          // S1 a pin 5  
#define S2 6          // S2 a pin 6
#define S3 7          // S3 a pin 7
#define salidaTCS 8   // salidaTCS a pin 8

// Variables globales
bool captureMode = false;
int totalReadings = 40;
int filteredReadings = 20;
int startIndex = 10;

// Arrays para almacenar todas las lecturas
int redValues[40];
int greenValues[40];
int blueValues[40];

void setup() {
  // Configuración de pines
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(salidaTCS, INPUT);
  
  // Establece frecuencia de salida al 20%
  digitalWrite(S0, HIGH);
  digitalWrite(S1, LOW);
  
  // Inicializa comunicación serie
  Serial.begin(9600);
  
  // Mensaje de inicio
  Serial.println("{\"status\":\"ready\",\"sensor\":\"TCS3200\",\"project\":\"color_collection\"}");
}

void loop() {
  // Escucha comandos desde Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "START_CAPTURE") {
      startColorCapture();
    }
    else if (command == "GET_STATUS") {
      Serial.println("{\"status\":\"ready\",\"capture_mode\":false}");
    }
    else if (command == "CALIBRATE") {
      calibrateSensor();
    }
    else if (command == "SINGLE_READ") {
      singleColorReading();
    }
  }
  
  delay(100); // Pequeña pausa para no saturar
}

void startColorCapture() {
  Serial.println("{\"status\":\"starting_capture\",\"total_readings\":40}");
  
  // Capturar 40 mediciones
  for (int i = 0; i < totalReadings; i++) {
    // Progreso cada 10 lecturas
    if (i % 10 == 0) {
      Serial.println("{\"progress\":" + String((i * 100) / totalReadings) + ",\"reading\":" + String(i) + "}");
    }
    
    // Leer RGB
    redValues[i] = readColor('R');
    delay(50);
    greenValues[i] = readColor('G');
    delay(50);
    blueValues[i] = readColor('B');
    delay(50);
  }
  
  // Filtrar y enviar datos centrales (20 de 40)
  sendFilteredData();
  
  Serial.println("{\"status\":\"capture_complete\"}");
}

int readColor(char color) {
  switch(color) {
    case 'R':
      digitalWrite(S2, LOW);   // Filtro rojo
      digitalWrite(S3, LOW);
      break;
    case 'G':
      digitalWrite(S2, HIGH);  // Filtro verde
      digitalWrite(S3, HIGH);
      break;
    case 'B':
      digitalWrite(S2, LOW);   // Filtro azul
      digitalWrite(S3, HIGH);
      break;
  }
  
  delay(10); // Estabilización
  
  // Promedio de 3 lecturas para mayor precisión
  int total = 0;
  for (int i = 0; i < 3; i++) {
    total += pulseIn(salidaTCS, LOW);
    delayMicroseconds(100);
  }
  
  return total / 3;
}

void sendFilteredData() {
  Serial.println("{\"filtered_data\":{");
  
  // Enviar valores R filtrados
  Serial.print("\"red\":[");
  for (int i = startIndex; i < startIndex + filteredReadings; i++) {
    Serial.print(redValues[i]);
    if (i < startIndex + filteredReadings - 1) Serial.print(",");
  }
  Serial.println("],");
  
  // Enviar valores G filtrados
  Serial.print("\"green\":[");
  for (int i = startIndex; i < startIndex + filteredReadings; i++) {
    Serial.print(greenValues[i]);
    if (i < startIndex + filteredReadings - 1) Serial.print(",");
  }
  Serial.println("],");
  
  // Enviar valores B filtrados
  Serial.print("\"blue\":[");
  for (int i = startIndex; i < startIndex + filteredReadings; i++) {
    Serial.print(blueValues[i]);
    if (i < startIndex + filteredReadings - 1) Serial.print(",");
  }
  Serial.println("]");
  
  // Calcular y enviar promedios
  float avgRed = calculateAverage(redValues, startIndex, filteredReadings);
  float avgGreen = calculateAverage(greenValues, startIndex, filteredReadings);
  float avgBlue = calculateAverage(blueValues, startIndex, filteredReadings);
  
  Serial.println(",\"averages\":{");
  Serial.println("\"red\":" + String(avgRed) + ",");
  Serial.println("\"green\":" + String(avgGreen) + ",");
  Serial.println("\"blue\":" + String(avgBlue));
  Serial.println("}}}");
}

float calculateAverage(int values[], int start, int count) {
  float sum = 0;
  for (int i = start; i < start + count; i++) {
    sum += values[i];
  }
  return sum / count;
}

void singleColorReading() {
  int r = readColor('R');
  int g = readColor('G');
  int b = readColor('B');
  
  Serial.println("{\"single_reading\":{\"red\":" + String(r) + ",\"green\":" + String(g) + ",\"blue\":" + String(b) + "}}");
}

void calibrateSensor() {
  Serial.println("{\"status\":\"calibrating\"}");
  
  // Calibración básica - lectura de referencia
  Serial.println("{\"calibration\":\"place_white_reference\"}");
  delay(3000);
  
  int whiteR = readColor('R');
  int whiteG = readColor('G');
  int whiteB = readColor('B');
  
  Serial.println("{\"white_reference\":{\"red\":" + String(whiteR) + ",\"green\":" + String(whiteG) + ",\"blue\":" + String(whiteB) + "}}");
  
  Serial.println("{\"calibration\":\"complete\"}");
}