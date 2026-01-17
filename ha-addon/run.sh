#!/usr/bin/env bash
echo "Starting ESP32 BLE Presence Addon..."

python3 - <<'EOF'
from flask import Flask, jsonify, request, send_from_directory
import paho.mqtt.client as mqtt
import os

app = Flask(__name__, static_folder="www")

# Load options from environment (HA injectib)
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'mqtt://core-mosquitto')
ZIGBEE_TOPIC = os.environ.get('ZIGBEE_TOPIC', 'zigbee/presence')
SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL_SEC', 6))
RSSI_THRESHOLD = int(os.environ.get('RSSI_THRESHOLD', -70))

# MQTT client
client = mqtt.Client()
client.connect("core-mosquitto", 1883, 60)

# Dummy device state
devices = {
    "esp32_node_1": {"name": "Living Room", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None},
    "esp32_node_2": {"name": "Bedroom", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None}
}

# Dummy users / people
users = {
    "Taavi": {"devices": [{"id":"SM-G986B","name":"Telefon"}, {"id":"KT-001","name":"Nutikell"}]},
    "Juku": {"devices": [{"id":"SM-F731B","name":"Telefon"}]}
}

# Routes

# Serve frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/logo.png")
def logo():
    return send_from_directory(app.static_folder, "logo.png")

# Get devices
@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

# Update device
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

# Heartbeat
@app.route("/heartbeat/<device_id>", methods=["POST"])
def heartbeat(device_id):
    if device_id not in devices:
        return jsonify({"error": "Unknown device"}), 404
    devices[device_id]["last_seen"] = "now"
    return jsonify({"status": "ok"})

# Users
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
EOF
