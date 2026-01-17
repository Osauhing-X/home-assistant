import threading
import time
import paho.mqtt.client as mqtt

ble_devices = []  # Shared state, Flask saab seda lugeda

def mqtt_thread():
    client = mqtt.Client()
    try:
        client.connect("core-mosquitto", 1883, 60)
        client.loop_start()
        while True:
            # Siia lisa ESP32 BLE andmete lugemine
            # Näiteks ble_devices.append({"name": "ESP32", "rssi": -70})
            time.sleep(5)
    except Exception as e:
        print("MQTT ei ole saadaval:", e)
