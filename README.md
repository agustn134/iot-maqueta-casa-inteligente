# 🏠 Proyecto IoT: Casa Inteligente con Alumbrado Público

Este proyecto consiste en una maqueta de una casa inteligente que utiliza sensores KY, PIR, pantallas OLED y ESP32 para detectar eventos como fuego, movimiento, luz, temperatura y más. La información recolectada se transmite mediante MQTT hacia Node-RED, donde se almacena en una base de datos PostgreSQL local y se visualiza en tiempo real.

---

## 🎥 Videos del Proyecto

- ✅ [Prueba de Funcionamiento del Proyecto](https://youtu.be/kPyg2eJ0VYg?si=wpGCY4Vnu6hMVZsQ)
- 🧑‍🏫 [Persona Externa que Aprueba el Proyecto](https://youtu.be/j4nz-pYEb0M?si=YJegoRfjVuyzQKbG)

---

## 🧠 Arquitectura del Proyecto

- 4 placas **ESP32**, cada una conectada a diferentes sensores y actuadores.
- **Comunicación por MQTT** utilizando `broker.emqx.io`.
- **Node-RED** ejecutándose localmente en la laptop para:
  - Recibir mensajes MQTT.
  - Almacenar lecturas en **PostgreSQL**.
  - Visualizar datos y estado del sistema.
- 2 pantallas **OLED SSD1306 (I2C)** para mostrar información local.
- Automatización del **alumbrado público con sensor PIR**.

---

## 🔧 Tecnologías y Componentes Usados

- **Lenguaje:** Python (con Thonny)
- **Microcontroladores:** ESP32 (x4)
- **Red:** MQTT (EMQX Broker público)
- **Base de Datos:** PostgreSQL
- **Visualización:** Node-RED
- **Sensores KY y módulos comunes:**
  - MQ2 (gas/humo), KY-036, KY-015, KY-026, KY-018, KY-032, PIR, botón push
- **Actuadores:** LEDs, buzzer, pantallas OLED 0.96"

---

## 🧩 Distribución de Sensores y Responsables

| ID | Nombre                | Tipo     | Ubicación   | Responsable |
|----|-----------------------|----------|-------------|-------------|
| 1  | Sensor de Gas/Humo    | MQ2      | Sala        | Mane        |
| 2  | Sensor Táctil         | KY-036   | Entrada     | Mane        |
| 3  | Sensor Temp/Hum       | KY-015   | Dormitorio  | Agustin     |
| 4  | Sensor de Flama       | KY-026   | Cocina      | Agustin     |
| 5  | Buzzer                | KY-012   | Cocina      | Agustin     |
| 6  | Sensor de Luz         | KY-018   | Pasillo     | Meño        |
| 7  | Sensor de Proximidad  | KY-032   | Pasillo     | Meño        |
| 8  | Sensor PIR            | HC-SR501 | Poste       | General     |
| 9  | Botón Push            | Genérico | Entrada     | General     |

---

## 🗃️ Estructura de Base de Datos (PostgreSQL)

### `sensores`

| Columna     | Tipo                   | Nulable | Por omisión                     |
|-------------|------------------------|---------|---------------------------------|
| id          | integer                | no      | nextval('sensores_id_seq')     |
| nombre      | varchar(100)           | no      |                                 |
| tipo        | varchar(100)           | sí      |                                 |
| ubicacion   | varchar(100)           | sí      |                                 |
| responsable | varchar(50)            | sí      |                                 |

### `lecturas_sensor`

| Columna     | Tipo                         | Nulable | Por omisión                          |
|-------------|------------------------------|---------|--------------------------------------|
| id          | integer                      | no      | nextval('lecturas_sensor_id_seq')   |
| sensor_id   | integer (foreign key)        | no      |                                      |
| fecha_hora  | timestamp without time zone  | sí      | CURRENT_TIMESTAMP                    |
| valor       | text                         | sí      |                                      |

---

## 📂 Estructura del Repositorio

iot-maqueta-casa-inteligente/ │
├── README.md 
├── LICENSE 
├── .gitignore │ 
├── docs/ │ 
├── diagrama_general.png │ 
├── flujo_node_red.png │ 
└── fotos_maqueta/ │
├── maqueta_fisica.jpg │ 
└── sensores_conectados.jpg │ 
├── scripts/ │ 
├── sala.py # MQ2 y táctil │ 
├── cocina.py # Temp/Hum, flama, buzzer 
│ ├── alumbrado_pir.py # PIR con LEDs │ 
└── alumbrado_control.py # LEDs por botón o lógica │
├── sql/ │ 
└── iot_maqueta.sql │ 
├── node-red/ │
└── flujo-sensores.json │ 
└── datos/ └── mensajes_mqtt_ejemplo.json


---

## 💬 Formato de mensajes MQTT

Ejemplo de mensaje enviado desde un ESP32 a Node-RED:

```json
{
  "sensor_id": 4,
  "valor": "FUEGO DETECTADO"
}

