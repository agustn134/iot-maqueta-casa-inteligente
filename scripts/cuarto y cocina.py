# Código para flama, temp/hum, buzzer

from machine import Pin, I2C
import time
import dht
import ssd1306
import network
import json
from umqtt.simple import MQTTClient

# === CONFIGURACIÓN WIFI Y MQTT ===
SSID = 'INFINITUM2A4D_2.4'
PASSWORD = 'uTDmnG5K9S'
MQTT_CLIENT_ID = 'esp32_cocina'
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_USER = ''
MQTT_PASSWORD = ''
MQTT_TOPIC_FIRE = b'esp32/sensor_fuego'   
MQTT_TOPIC_TEMP = b'esp32/temp_hum'        

sensor_flama = Pin(18, Pin.IN)
sensor_temp = dht.DHT11(Pin(4))
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
led_amarillo = Pin(19, Pin.OUT)
led_rojo = Pin(23, Pin.OUT)
buzzer = Pin(5, Pin.OUT)

# === VARIABLES GLOBALES ===
temp = 0
hum = 0
ultimo_tiempo_dht = 0
intervalo_dht = 2000  # 2 segundos entre lecturas de DHT11
ultima_actualizacion_oled = 0
intervalo_oled = 1000  # 1 segundo entre actualizaciones de OLED
ultimo_envio_temp_hum = 0
intervalo_temp_hum = 5000  # 5 segundos entre envíos de temp/hum
fuego_detectado = False
ultima_notificacion_fuego = 0
wifi_conectado = False
mqtt_client = None

# === FUNCIONES DE CONEXION ===
def conectar_wifi():
    global wifi_conectado
    
    oled.fill(0)
    oled.text("Conectando a", 10, 10)
    oled.text("WiFi...", 10, 30)
    oled.show()
    
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    
    # Esperar hasta 20 segundos para la conexion
    max_espera = 20
    while max_espera > 0 and not wifi.isconnected():
        max_espera -= 1
        oled.fill(0)
        oled.text("Conectando", 10, 10)
        oled.text("WiFi... {}".format(max_espera), 10, 30)
        oled.show()
        time.sleep(1)
    
    if wifi.isconnected():
        print("Conectado a WiFi:", SSID)
        print("IP:", wifi.ifconfig()[0])
        wifi_conectado = True
        oled.fill(0)
        oled.text("WiFi Conectado!", 10, 20)
        oled.text(wifi.ifconfig()[0], 10, 40)
        oled.show()
        time.sleep(2)
        return True
    else:
        print("Error de conexión WiFi")
        wifi_conectado = False
        oled.fill(0)
        oled.text("Error WiFi", 10, 30)
        oled.show()
        time.sleep(2)
        return False

def llegada_mensaje(topic, msg):
    print("Mensaje MQTT recibido:", topic, msg)
    mensaje = msg.decode('utf-8')
    
    # Controlar LEDs segun comandos recibidos
    if mensaje == "1":
        led_amarillo.on()
        print("LED encendido por comando")
    elif mensaje == "0":
        led_amarillo.off()
        print("LED apagado por comando")

def conectar_mqtt():
    global mqtt_client
    
    try:
        print("Conectando a MQTT broker:", MQTT_BROKER)
        oled.fill(0)
        oled.text("Conectando MQTT", 10, 30)
        oled.show()
        
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, 
                          user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
        client.set_callback(llegada_mensaje)
        client.connect()
        client.subscribe(MQTT_TOPIC_FIRE)
        
        print("Conexión MQTT exitosa")
        oled.fill(0)
        oled.text("MQTT Conectado!", 10, 30)
        oled.show()
        time.sleep(1)
        
        return client
    except Exception as e:
        print("Error en conexión MQTT:", e)
        oled.fill(0)
        oled.text("Error MQTT:", 10, 20)
        oled.text(str(e), 10, 35)
        oled.show()
        time.sleep(2)
        return None

# === FUNCIONES DE PANTALLA OLED ===
def actualizar_oled():
    oled.fill(0)
    oled.text("MONITOR FUEGO", 10, 0)
    
    # Mostrar temperatura y humedad
    oled.text("Temp: {} C".format(temp), 10, 20)
    oled.text("Hum: {} %".format(hum), 10, 30)
    
    # Estado del sensor de flama con enfoque principal
    if sensor_flama.value() == 1:
        oled.fill_rect(0, 45, 128, 19, 1)  
        oled.text("FUEGO DETECTADO!", 5, 50, 0)  
    else:
        oled.text("Estado: Normal", 10, 50)
    
    # Mostrar estado de conexion
    if wifi_conectado:
        oled.text("WiFi: OK", 70, 10)
    else:
        oled.text("WiFi: NO", 70, 10)
    
    oled.show()

# === INICIALIZACION ===
led_amarillo.off()
led_rojo.off()
buzzer.off()

# Mostrar pantalla de bienvenida
oled.fill(0)
oled.text("Sistema de", 20, 10)
oled.text("Deteccion de", 10, 25)
oled.text("FUEGO", 40, 40)
oled.show()
time.sleep(2)

# Conectar WiFi
if conectar_wifi():
    mqtt_client = conectar_mqtt()

while True:
    tiempo_actual = time.ticks_ms()
    
    # Reconectar WiFi si se perdio la conexion
    if not wifi_conectado and time.ticks_diff(tiempo_actual, ultimo_tiempo_dht) >= 30000:
        conectar_wifi()
        if wifi_conectado:
            mqtt_client = conectar_mqtt()
        ultimo_tiempo_dht = tiempo_actual
    
    # Verificar sensor de flama en cada iteracion
    fuego_actual = sensor_flama.value() == 1
    
    # DETECCION DE FUEGO - PARTE PRINCIPAL
    if fuego_actual:
        print("¡FUEGO DETECTADO!")
        led_amarillo.off()
        led_rojo.on()
        
        # Sonido de alarma
        buzzer.on()
        time.sleep(0.2)
        buzzer.off()
        time.sleep(0.1)
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        
        # Solo enviar si ha pasado suficiente tiempo desde la ultima notificacion
        if mqtt_client and (not fuego_detectado or time.ticks_diff(tiempo_actual, ultima_notificacion_fuego) >= 5000):
            try:
                print("Enviando alerta de fuego por MQTT")
                mqtt_client.publish(MQTT_TOPIC_FIRE, b'fuego')
                ultima_notificacion_fuego = tiempo_actual
                fuego_detectado = True
            except Exception as e:
                print("Error al enviar alerta de fuego:", e)
    
    # Si ya no hay fuego pero estabamos en estado de alerta
    elif fuego_detectado and not fuego_actual:
        print("Fuego controlado - volviendo a normal")
        led_rojo.off()
        led_amarillo.on()
        
        # Enviar mensaje de normalidad
        if mqtt_client:
            try:
                mqtt_client.publish(MQTT_TOPIC_FIRE, b'normal')
                print("Enviado mensaje 'normal' al broker")
                fuego_detectado = False
            except Exception as e:
                print("Error al enviar estado normal:", e)
    
    # Estado normal sin fuego
    elif not fuego_actual:
        led_rojo.off()
        led_amarillo.on()
    
    if time.ticks_diff(tiempo_actual, ultimo_tiempo_dht) >= intervalo_dht:
        try:
            sensor_temp.measure()
            temp = sensor_temp.temperature()
            hum = sensor_temp.humidity()
            print("Temp: {} °C | Hum: {} %".format(temp, hum))
            ultimo_tiempo_dht = tiempo_actual
        except Exception as e:
            print("Error DHT11:", e)
    
    # Enviar datos de temperatura y humedad 
    if mqtt_client and time.ticks_diff(tiempo_actual, ultimo_envio_temp_hum) >= intervalo_temp_hum:
        try:
            # Crear objeto JSON 
            datos_json = {
                "temperature": temp,
                "humidity": hum
            }
            
            # Convertir a string JSON
            json_str = json.dumps(datos_json)
            
            mqtt_client.publish(MQTT_TOPIC_TEMP, json_str)
            print("Datos enviados al broker - Temp:", temp, "°C, Hum:", hum, "%")
            
            # Actualizar timestamp del ultimo envio
            ultimo_envio_temp_hum = tiempo_actual
        except Exception as e:
            print("Error al enviar temperatura y humedad:", e)
    
    # Actualizar OLED cada intervalo_oled 1 segundo
    if time.ticks_diff(tiempo_actual, ultima_actualizacion_oled) >= intervalo_oled:
        try:
            actualizar_oled()
            ultima_actualizacion_oled = tiempo_actual
        except Exception as e:
            print("Error OLED:", e)
            oled.fill(0)
            oled.text("Error pantalla", 10, 30)
            oled.show()
    
    # Verificar si hay mensajes MQTT pendientes
    if mqtt_client:
        try:
            mqtt_client.check_msg()
        except Exception as e:
            print("Error al revisar mensajes MQTT:", e)
            # Intentar reconectar MQTT
            mqtt_client = conectar_mqtt()
    
    # Pequeña pausa para no saturar el CPU
    time.sleep(0.1)
