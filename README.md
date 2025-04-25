# Proyecto IoT - Maqueta de Casa Inteligente con Alumbrado Público

Este proyecto simula una casa inteligente con sensores y actuadores conectados a 3 ESP32, y una cuarta ESP32 que opera como centro de monitoreo visual con una pantalla TFT 2.4". Los datos son enviados a un broker MQTT y almacenados en PostgreSQL a través de Node-RED.

## 🔧 Tecnologías
- ESP32 (4)
- Node-RED + MQTT Broker local
- PostgreSQL + SQLite (opcional)
- Python (Thonny)
- LVGL (pantalla TFT)
- Sensores KY, PIR, OLED SSD1306

## 📦 Estructura
- `scripts/`: Códigos Python y Arduino
- `docs/`: Diagramas y evidencias gráficas
- `sql/`: Script de base de datos
- `node-red/`: Flujos MQTT y base de datos
- `datos/`: Datos simulados y exportados

## 📋 Sensores Usados

| ID | Sensor                | Tipo     | Ubicación   | Responsable |
|----|-----------------------|----------|-------------|-------------|
| 1  | Sensor de Gas/Humo    | MQ2      | Sala        | Mane        |
| 2  | Sensor Táctil         | KY-036   | Entrada     | Mane        |
| 3  | Temp y Humedad        | KY-015   | Dormitorio  | Agustin     |
| 4  | Sensor de Flama       | KY-026   | Cocina      | Agustin     |
| 5  | Buzzer                | KY-012   | Cocina      | Agustin     |
| 6  | Fotoresistencia       | KY-018   | Pasillo     | Meño        |
| 7  | Sensor Proximidad     | KY-032   | Pasillo     | Meño        |
| 8  | Sensor PIR            | HC-SR501 | Poste       | Público     |
| 9  | Botón Push            | Genérico | Entrada     | General     |

## 📊 Vista general del sistema

- 3 ESP32 envían datos por MQTT
- 1 ESP32 recibe datos y los visualiza en pantalla LVGL
- Node-RED maneja base de datos PostgreSQL y dashboard web

## 📝 Autores

- Mane
- Agustin
- Meño
