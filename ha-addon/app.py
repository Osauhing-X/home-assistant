from flask import Flask, jsonify, request, send_from_directory
import paho.mqtt.client as mqtt
import os

app = Flask(__name__, static_folder="/www")

MQTT_BROKER = os.environ.get("MQTT_BROKER", "core-mosquitto")
ZIGBEE_TOPIC = os.environ.get("ZIGBEE_TOPIC", "zigbee/presence")
SCAN_INTERVAL = int(os.environ.get("SCAN_INTERVAL_SEC", 6))
RSSI_THRESHOLD = int(os.environ.get("RSSI_THRESHOLD", -70))

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

devices = {
    "esp32_node_1": {"name": "Living Room", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None},
    "esp32_node_2": {"name": "Bedroom", "rssi_threshold": RSSI_THRESHOLD, "last_seen": None}
}

users = {
    "Taavi": {"devices": [{"id":"SM-G986B","name":"Telefon"}]},
    "Juku": {"devices": [{"id":"SM-F731B","name":"Telefon"}]}
}

@app.route("/")
def index():
    return send_from_directory("/www", "index.html")

@app.route("/devices")
def get_devices():
    return jsonify(devices)

@app.route("/devices/<device_id>", methods=["POST"])
def update_device(device_id):
    data = request.json
    if device_id not in devices:
        return jsonify({"error": "Unknown device"}), 404

    if "rssi_threshold" in data:
        devices[device_id]["rssi_threshold"] = data["rssi_threshold"]

    client.publish(
        f"{ZIGBEE_TOPIC}/{device_id}",
        str({"rssi_threshold": devices[device_id]["rssi_threshold"]})
    )

    return jsonify(devices[device_id])

@app.route("/users")
def get_users():
    return jsonify(users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
