import paho.mqtt.client as mqtt
import time

BROKER = "test.mosquitto.org"
TOPIC = "esp32/ble"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    client.loop_stop()
