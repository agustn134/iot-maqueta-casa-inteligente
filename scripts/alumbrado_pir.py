# Código PIR y LEDs calle

from machine import Pin
from time import sleep, time

# Sensor PIR en GPIO27
pir = Pin(27, Pin.IN)

# Pines de los LEDs
led_pins = [13, 12, 14, 26, 25, 33, 32]
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

for led in leds:
    led.off()

leds_encendidos = False
tiempo_apagado = 0

TIEMPO_POR_DETECCION = 7

while True:
    if pir.value() == 1:
        print(" Movimiento detectado")

        if not leds_encendidos:
            print("Encendiendo LEDs")
            for led in leds:
                led.on()
            leds_encendidos = True

        # Actualiza el tiempo para apagar los LEDs
        tiempo_apagado = time() + TIEMPO_POR_DETECCION
        print(f"Tiempo extendido hasta: {tiempo_apagado} segundos ")
        sleep(0.5)  

    if leds_encendidos:
        if time() >= tiempo_apagado:
            print("Tiempo cumplido. Apagando LEDs")
            for led in leds:
                led.off()
            leds_encendidos = False

    sleep(0.1)
