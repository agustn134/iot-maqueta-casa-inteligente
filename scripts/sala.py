# Código para MQ2 y táctil
import urequests
import network
import ntptime
import time
from machine import Pin, I2C, RTC
import ssd1306
from umqtt.simple import MQTTClient 

# ————— Configuracion Wi‑Fi —————
SSID     = 'INFINITUM2A4D_2.4'
PASSWORD = 'uTDmnG5K9S'

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while not wifi.isconnected():
    time.sleep(0.2)

# ————— Configuracion MQTT —————
MQTT_CLIENT_ID = 'esp32_alerta'
MQTT_Broker = "broker.emqx.io"
MQTT_PORT      = 1883
MQTT_USER      = ''
MQTT_PASSWORD  = ''
MQTT_TOPIC     = b'esp32/gas'

# ————— Sincronizar hora —————
try:
    ntptime.settime()
except:
    pass

# ————— Inicializacion OLED —————
i2c  = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Asegurar que la pantalla está encendida al inicio
oled.fill(0)
oled.text("Iniciando...", 20, 30)
oled.show()

# ————— Pines y sensores —————
sensor_toque = Pin(18, Pin.IN)
led_entrada  = Pin(2,  Pin.OUT)
sensor_gas   = Pin(15, Pin.IN)
boton        = Pin(4, Pin.IN, Pin.PULL_UP)
led          = Pin(5, Pin.OUT)
estado_led   = False
ultimo_estado_boton = 1
tocando_anterior = False 

# ————— Horarios —————
UTC_MX    = -6 * 3600
UTC_CHINA =  8 * 3600
UTC_PARIS =  1 * 3600

def hora_str(desfase):
    t = time.localtime(time.time() + desfase)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

# ————— MQTT —————
def llegada_mensaje(topic, msg):
    print("=== MENSAJE MQTT RECIBIDO ===")
    print("Tópico:", topic)
    print("Mensaje:", msg)
    print("Tipo de mensaje:", type(msg))
    
    if msg == b'1':
        print("Intentando encender LED (pin 5)")
        led.value(1)
        print("LED debería estar encendido ahora")
    elif msg == b'0':
        print("Intentando apagar LED (pin 5)")
        led.value(0)
        print("LED debería estar apagado ahora")
    else:
        print("Mensaje no reconocido para control de LED")

def subscribir():
    try:
        print("Intentando conectar a MQTT broker:", MQTT_Broker)
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_Broker, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
        client.set_callback(llegada_mensaje)
        client.connect()
        print("Conexión MQTT exitosa")
        client.subscribe(MQTT_TOPIC)
        print("Suscrito al tópico:", MQTT_TOPIC)
        return client
    except Exception as e:
        print("Error en la conexión MQTT:", e)
        time.sleep(5)
        return None

def publicar_seguro(cliente, topico, mensaje):
    """Intenta publicar un mensaje MQTT de forma segura, manejando errores de conexión"""
    if cliente is None:
        print("No hay conexión MQTT para publicar")
        return False
    
    try:
        cliente.publish(topico, mensaje)
        return True
    except Exception as e:
        print("Error al publicar mensaje MQTT:", e)
        return False

# ————— Icono de campana —————
bell_icon = [
    "  ##  ",
    " #### ",
    "######",
    "######",
    "######",
    " #### ",
    "  ##  ",
    "  ##  ",
]

# ————— Inicio MQTT —————
mqtt_client = subscribir()
ultima_alerta = 0  
ultimo_estado_gas = False 
ultima_alerta_timbre = 0  

# Enviar estado inicial normal
if mqtt_client:
    try:
        mqtt_client.publish(MQTT_TOPIC, b'normal')
        print("Estado inicial enviado: normal")
    except:
        print("Error al enviar estado inicial")

# ————— Variables para pantalla —————
ultima_actualizacion_pantalla = 0
intervalo_refresh_pantalla = 500 

# ————— Bucle principal —————
ultimo_envio = 0  

while True:
    try:
        if not wifi.isconnected():
            print("WiFi desconectado, reconectando...")
            wifi.connect(SSID, PASSWORD)
            
            oled.fill(0)
            oled.text("Reconectando", 10, 20)
            oled.text("WiFi...", 30, 35)
            oled.show()
            
            time.sleep(5)
            continue
        
        if mqtt_client is None:
            print("Intentando reconectar a MQTT...")
            
            oled.fill(0)
            oled.text("Reconectando", 10, 20)
            oled.text("MQTT...", 30, 35)
            oled.show()
            
            mqtt_client = subscribir()
            time.sleep(2)
            continue
        
        try:
            mqtt_client.check_msg()  # Verifica mensajes entrantes
        except Exception as e:
            print("Error al verificar mensajes MQTT:", e)
            mqtt_client = None  # Forzar reconexión
            time.sleep(5)
            continue

        tocando   = sensor_toque.value() == 1
        gas_alert = sensor_gas.value() == 0
        tiempo_actual = time.time()
        
        # Comprobar cambio de estado de gas
        if gas_alert != ultimo_estado_gas:
            if gas_alert:
                print("¡ALERTA! Humo o gas detectado.")
                if mqtt_client:
                    try:
                        mqtt_client.publish(MQTT_TOPIC, b'alerta')
                        print("Alerta enviada correctamente")
                    except Exception as e:
                        print("Error al enviar alerta:", e)
            else:
                # Cambio a estado normal
                print("Estado normal restaurado después de alerta.")
                if mqtt_client:
                    try:
                        mqtt_client.publish(MQTT_TOPIC, b'normal')  
                        print("Estado normal enviado correctamente")
                    except Exception as e:
                        print("Error al enviar estado normal:", e)
            
            ultimo_estado_gas = gas_alert
            ultima_alerta = tiempo_actual
        
        # Comprobar timbre - Enviar mensaje solo cuando se activa el timbre
        # y limitar a una alerta cada 5 segundos para evitar spam
        if tocando and not tocando_anterior and tiempo_actual - ultima_alerta_timbre > 5:
            print("¡Alguien está tocando el timbre!")
            if mqtt_client:
                try:
                    mqtt_client.publish(MQTT_TOPIC, b'timbre')
                    print("Alerta de timbre enviada correctamente")
                    ultima_alerta_timbre = tiempo_actual
                except Exception as e:
                    print("Error al enviar alerta de timbre:", e)
        
        tocando_anterior = tocando  
        
        # Enviar estado periodicamente cada 60 segundos
        if tiempo_actual - ultimo_envio > 60:
            if gas_alert:
                publicar_seguro(mqtt_client, MQTT_TOPIC, b'alerta')
                print("Reenvío periódico: alerta")
            else:
                publicar_seguro(mqtt_client, MQTT_TOPIC, b'normal')
                print("Reenvío periódico: normal")
            ultimo_envio = tiempo_actual

        estado_boton = boton.value()
        if ultimo_estado_boton == 1 and estado_boton == 0:
            estado_led = not estado_led
            led.value(estado_led)
            print("LED botón:", "ENCENDIDO" if estado_led else "APAGADO")
            time.sleep(0.2)

        ultimo_estado_boton = estado_boton

        # Actualizar la pantalla regularmente para asegurar que siempre este encendida
        tiempo_actual_ms = time.ticks_ms()
        if time.ticks_diff(tiempo_actual_ms, ultima_actualizacion_pantalla) >= intervalo_refresh_pantalla:
            oled.fill(0)  # Limpiar pantalla

            if tocando:
                oled.text("Estan tocando",  0, 0)
                oled.text("el timbre",      0, 10)
                x0, y0 = 85, 8
                for y, row in enumerate(bell_icon):
                    for x, c in enumerate(row):
                        if c == "#":
                            oled.pixel(x0 + x, y0 + y, 1)
                led_entrada.on()

            elif gas_alert:
                oled.text("! ALARMA GAS !",   0, 0)
                oled.text("Humo/Gas detect.", 0, 16)
                led_entrada.off()

            else:
                oled.text("Bienvenido :)",           0, 0)
                oled.text("MX: " + hora_str(UTC_MX),    0, 16)
                oled.text("CN: " + hora_str(UTC_CHINA), 0, 26)
                oled.text("PAR: "+ hora_str(UTC_PARIS), 0, 36)
                led_entrada.off()
            
            # Indicador de estado de conexiones
            if wifi.isconnected():
                oled.text("WiFi: OK", 0, 54)
            else:
                oled.text("WiFi: NO", 0, 54)
                
            if mqtt_client is not None:
                oled.text("MQTT: OK", 70, 54)
            else:
                oled.text("MQTT: NO", 70, 54)
            
            # Asegurar que la pantalla se actualiza
            oled.show()
            ultima_actualizacion_pantalla = tiempo_actual_ms
            
        # Pequeña pausa para evitar sobrecarga del CPU
        time.sleep(0.1)
        
    except Exception as e:
        # Manejo de errores general para evitar que el programa se detenga
        print("Error en el bucle principal:", e)
        
        # Mostrar error en pantalla
        oled.fill(0)
        oled.text("ERROR:", 0, 20)
        oled.text(str(e)[:16], 0, 35)  
        oled.show()
        
        time.sleep(2)
