# Control de LEDs con botón

from machine import Pin
import network
import time
from umqtt.simple import MQTTClient

# ————— Configuración Wi‑Fi —————
SSID = 'INFINITUM2A4D_2.4'
PASSWORD = 'uTDmnG5K9S'

# ————— Configuración MQTT —————
MQTT_CLIENT_ID = 'esp32_focos_afuera'
MQTT_Broker = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_USER = ''
MQTT_PASSWORD = ''
MQTT_TOPIC = b'esp32/focos-afuera'

# ————— Configuración de LEDs —————
led_1 = Pin(13, Pin.OUT)
led_2 = Pin(12, Pin.OUT)
led_3 = Pin(14, Pin.OUT)
led_4 = Pin(27, Pin.OUT)

# ————— Estado inicial de los LEDs y inicialmente todos apagados —————
led_states = [False, False, False, False]  
leds = [led_1, led_2, led_3, led_4]

# ————— Funciones para control de LEDs —————
def set_all_leds(state):
    """Enciende o apaga todos los LEDs"""
    for i, led in enumerate(leds):
        led.value(1 if state else 0)
        led_states[i] = state
    print(f"🔄 Todos los LEDs {'ENCENDIDOS' if state else 'APAGADOS'}")

def set_led(led_num, state):
    """Enciende o apaga un LED específico"""
    if 1 <= led_num <= 4:
        leds[led_num-1].value(1 if state else 0)
        led_states[led_num-1] = state
        print(f"🔄 LED {led_num} {'ENCENDIDO' if state else 'APAGADO'}")
    else:
        print(f"❌ LED {led_num} no existe")

# ————— Función para recibir mensajes MQTT —————
def llegada_mensaje(topic, msg):
    """Procesa mensajes MQTT recibidos"""
    print(f"📩 Mensaje recibido: {msg}")
    
    try:
        # Convertir a string para facilitar el procesamiento
        comando = msg.decode('utf-8').strip()
        
        # Comandos para todos los LEDs
        if comando == "all_on":
            set_all_leds(True)
        elif comando == "all_off":
            set_all_leds(False)
        elif comando.startswith("led") and (comando.endswith("_on") or comando.endswith("_off")):
            parts = comando.split("_")
            led_num = int(parts[0][3:])  # Extraer número después de "led"
            state = parts[1] == "on"
            set_led(led_num, state)
        # Estado actual
        elif comando == "status":
            publish_status()
        else:
            print(f"Comando no reconocido: {comando}")
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")

def publish_status():
    """Publica el estado actual de todos los LEDs"""
    if mqtt_client:
        try:
            status = ','.join([f"led{i+1}:{'on' if state else 'off'}" for i, state in enumerate(led_states)])
            mqtt_client.publish(MQTT_TOPIC + b'/status', status.encode())
            print(f" Estado publicado: {status}")
        except Exception as e:
            print(f" Error al publicar estado: {e}")

# ————— Conexión WiFi —————
print("Conectando a WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# Esperar a que se conecte
max_wait = 20
while max_wait > 0 and not wifi.isconnected():
    print(f"Esperando conexión... {max_wait}s")
    time.sleep(1)
    max_wait -= 1

if wifi.isconnected():
    print(f"Conectado a WiFi: {SSID}")
    print(f"IP: {wifi.ifconfig()[0]}")
else:
    print("No se pudo conectar a WiFi")
    raise RuntimeError('No se pudo conectar a la red WiFi')

# ————— Conexion MQTT —————
mqtt_client = None

def conectar_mqtt():
    """Establece conexion con el broker MQTT"""
    global mqtt_client
    
    try:
        print(f"Conectando a MQTT broker: {MQTT_Broker}")
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_Broker, port=MQTT_PORT, 
                          user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
        client.set_callback(llegada_mensaje)
        client.connect()
        print("Conexión MQTT exitosa")
        
        # Suscribirse al topico
        client.subscribe(MQTT_TOPIC)
        print(f"Suscrito al tópico: {MQTT_TOPIC}")
        
        # Publicar estado inicial
        client.publish(MQTT_TOPIC + b'/status', "ready".encode())
        
        return client
    except Exception as e:
        print(f"Error en conexión MQTT: {e}")
        return None

# ————— Inicializacion —————
print("Iniciando sistema de control de focos...")
mqtt_client = conectar_mqtt()

if mqtt_client:
    print("Sistema listo para recibir comandos")
else:
    print("Sistema iniciado sin MQTT, intentando reconectar...")

ultima_reconexion = 0
ultimo_envio_estado = 0

# ————— Bucle principal —————
try:
    while True:
        tiempo_actual = time.time()
        
        # Verificar conexion WiFi
        if not wifi.isconnected():
            print("WiFi desconectado, reconectando...")
            wifi.connect(SSID, PASSWORD)
            time.sleep(5)
            continue
        
        # Verificar/reconectar MQTT
        if mqtt_client is None and tiempo_actual - ultima_reconexion > 10:
            print("Intentando reconectar MQTT...")
            mqtt_client = conectar_mqtt()
            ultima_reconexion = tiempo_actual
        
        # Procesar mensajes MQTT
        if mqtt_client:
            try:
                mqtt_client.check_msg()
            except Exception as e:
                print(f"Error al verificar mensajes MQTT: {e}")
                mqtt_client = None
                continue
        
        # Publicar estado periodicamente (cada 30 segundos)
        if mqtt_client and tiempo_actual - ultimo_envio_estado > 30:
            publish_status()
            ultimo_envio_estado = tiempo_actual
        
        # Pausa para no sobrecargar el CPU
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    
finally:
    # Apagar todos los LEDs antes de salir
    print("Limpiando antes de salir...")
    set_all_leds(False)
