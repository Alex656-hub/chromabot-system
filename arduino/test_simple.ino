/*
  Chromabot - Test Simple del TCS3200
  Para verificar comunicación básica y lectura de sensor
*/

#define S0 4          
#define S1 5          
#define S2 6          
#define S3 7          
#define salidaTCS 8   

void setup() {
  // Configuración de pines
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(salidaTCS, INPUT);
  
  // Frecuencia al 20%
  digitalWrite(S0, HIGH);
  digitalWrite(S1, LOW);
  
  Serial.begin(9600);
  
  // Mensaje de inicio
  Serial.println("=== CHROMABOT TEST INICIADO ===");
  Serial.println("Comandos disponibles:");
  Serial.println("1 - Lectura simple RGB");
  Serial.println("2 - Test continuo");
  Serial.println("3 - Status");
}

void loop() {
  // Lectura automática cada 2 segundos
  static unsigned long lastReading = 0;
  if (millis() - lastReading > 2000) {
    readColorSimple();
    lastReading = millis();
  }
  
  // Procesar comandos del serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    Serial.println("Comando recibido: " + command);
    
    if (command == "1") {
      Serial.println("=== LECTURA RGB SIMPLE ===");
      readColorDetailed();
    }
    else if (command == "2") {
      Serial.println("=== TEST CONTINUO (10 lecturas) ===");
      for (int i = 0; i < 10; i++) {
        Serial.print("Lectura " + String(i+1) + ": ");
        readColorSimple();
        delay(500);
      }
    }
    else if (command == "3") {
      Serial.println("=== STATUS DEL SISTEMA ===");
      Serial.println("Arduino: OK");
      Serial.println("Sensor TCS3200: Conectado en pines 4-8");
      Serial.println("Comunicacion: Activa a 9600 bps");
    }
    else if (command == "GET_STATUS") {
      Serial.println("{\"status\":\"ready\",\"sensor\":\"TCS3200\",\"test\":\"OK\"}");
    }
    else if (command == "SINGLE_READ") {
      readColorJSON();
    }
    else {
      Serial.println("Comando no reconocido: " + command);
      Serial.println("Usa: 1, 2, 3, GET_STATUS, o SINGLE_READ");
    }
  }
}

void readColorSimple() {
  int r = readChannel('R');
  int g = readChannel('G');
  int b = readChannel('B');
  
  Serial.print("RGB: ");
  Serial.print(r);
  Serial.print(", ");
  Serial.print(g);
  Serial.print(", ");
  Serial.println(b);
}

void readColorDetailed() {
  Serial.println("Leyendo ROJO...");
  int r = readChannel('R');
  delay(100);
  
  Serial.println("Leyendo VERDE...");
  int g = readChannel('G');
  delay(100);
  
  Serial.println("Leyendo AZUL...");
  int b = readChannel('B');
  delay(100);
  
  Serial.println("Resultados:");
  Serial.println("Rojo: " + String(r));
  Serial.println("Verde: " + String(g));
  Serial.println("Azul: " + String(b));
  
  // Detección simple de color dominante
  if (r > g && r > b) {
    Serial.println("Color dominante: ROJO");
  } else if (g > r && g > b) {
    Serial.println("Color dominante: VERDE");
  } else if (b > r && b > g) {
    Serial.println("Color dominante: AZUL");
  } else {
    Serial.println("Color: NEUTRO/MIXTO");
  }
}

void readColorJSON() {
  int r = readChannel('R');
  int g = readChannel('G');
  int b = readChannel('B');
  
  Serial.print("{\"rgb\":{\"red\":");
  Serial.print(r);
  Serial.print(",\"green\":");
  Serial.print(g);
  Serial.print(",\"blue\":");
  Serial.print(b);
  Serial.println("}}");
}

int readChannel(char color) {
  // Configurar filtros según el color
  switch(color) {
    case 'R':
      digitalWrite(S2, LOW);   
      digitalWrite(S3, LOW);
      break;
    case 'G':
      digitalWrite(S2, HIGH);  
      digitalWrite(S3, HIGH);
      break;
    case 'B':
      digitalWrite(S2, LOW);   
      digitalWrite(S3, HIGH);
      break;
  }
  
  delay(50); // Tiempo de estabilización
  
  // Leer pulso
  int pulseWidth = pulseIn(salidaTCS, LOW, 100000); // timeout 100ms
  
  if (pulseWidth == 0) {
    Serial.println("ERROR: No se detecta señal del sensor");
    return -1;
  }
  
  return pulseWidth;
}