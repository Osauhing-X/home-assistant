import threading
import time
import os
import paho.mqtt.client as mqtt

def mqtt_loop():
    client = mqtt.Client()
    broker = os.environ.get('MQTT_BROKER', 'core-mosquitto')
    while True:
        try:
            client.connect(broker, 1883, 60)
            print("MQTT connected")
            client.loop_forever()
        except Exception as e:
            print(f"MQTT not ready, retry in 5s: {e}")
            time.sleep(5)

threading.Thread(target=mqtt_loop, daemon=True).start()
