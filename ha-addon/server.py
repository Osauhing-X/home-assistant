from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import os

app = Flask(__name__)

MQTT_BROKER = os.environ.get('MQTT_BROKER', 'core-mosquitto')
ZIGBEE_TOPIC = os.environ.get('ZIGBEE_TOPIC', 'zigbee/presence')

client = mqtt.Client()
client.connect("core-mosquitto", 1883, 60)

devices = {
    "esp32_node_1": {"name": "Living Room", "last_seen": None},
    "esp32_node_2": {"name": "Bedroom", "last_seen": None}
}

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/heartbeat/<device_id>", methods=["POST"])
def heartbeat(device_id):
    if device_id in devices:
        devices[device_id]["last_seen"] = "now"
        return jsonify({"status": "ok"})
    return jsonify({"error": "Unknown device"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
