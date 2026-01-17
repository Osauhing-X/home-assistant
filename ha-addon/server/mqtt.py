import time
import paho.mqtt.client as mqtt

BROKER = "core-mosquitto"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect

# Oota kuni broker saadaval
while True:
    try:
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print(f"Waiting for MQTT broker {BROKER}... ({e})")
        time.sleep(5)

client.loop_start()

# Näidis loop
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
