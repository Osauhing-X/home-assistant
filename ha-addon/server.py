from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import os
import socket
import time

app = Flask(__name__)

# MQTT seadistused
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'core-mosquitto')
BROKER_PORT = 1883
ZIGBEE_TOPIC = os.environ.get('ZIGBEE_TOPIC', 'zigbee/presence')
SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL_SEC', 6))
RSSI_THRESHOLD = int(os.environ.get('RSSI_THRESHOLD', -70))

# Oota, kuni MQTT broker on nähtav
while True:
    try:
        socket.gethostbyname(MQTT_BROKER)
        print(f"MQTT broker {MQTT_BROKER} is reachable")
        break
    except socket.gaierror:
        print(f"Waiting for MQTT broker {MQTT_BROKER}...")
        time.sleep(3)

# Loo MQTT client ja connect retry loop
client = mqtt.Client()
connected = False
while not connected:
    try:
        client.connect(MQTT_BROKER, BROKER_PORT, 60)
        connected = True
        print("Connected to MQTT broker")
    except Exception as e:
        print(f"MQTT connect failed: {e}, retrying in 3s...")
        time.sleep(3)

# Seadista seadmed ja kasutajad
devices = {
    "esp32_node_1": {"name": "Living Room", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None},
    "esp32_node_2": {"name": "Bedroom", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None}
}

users = {
    "Taavi": {"devices": [{"id":"SM-G986B","name":"Telefon"}, {"id":"KT-001","name":"Nutikell"}]},
    "Juku": {"devices": [{"id":"SM-F731B","name":"Telefon"}]}
}

# API endpointid
@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/devices/<device_id>", methods=["POST"])
def update_device(device_id):
    data = request.json
    if device_id not in devices:
        return jsonify({"error": "Unknown device"}), 404
    for key in ["name", "rssi_threshold"]:
        if key in data:
            devices[device_id][key] = data[key]
    payload = {"type": "config", "rssi_threshold": devices[device_id]["rssi_threshold"]}
    client.publish(f"{ZIGBEE_TOPIC}/{device_id}", str(payload))
    return jsonify(devices[device_id])

@app.route("/heartbeat/<device_id>", methods=["POST"])
def heartbeat(device_id):
    if device_id not in devices:
        return jsonify({"error": "Unknown device"}), 404
    devices[device_id]["last_seen"] = "now"
    return jsonify({"status": "ok"})

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users/<user_name>/devices", methods=["POST"])
def add_user_device(user_name):
    data = request.json
    if user_name not in users:
        users[user_name] = {"devices": []}
    users[user_name]["devices"].append(data)
    return jsonify(users[user_name])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
