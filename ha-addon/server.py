from flask import Flask, jsonify, request
import threading
import time
import os

app = Flask(__name__)

# Dummy devices
devices = {
    "esp32_node_1": {"name": "Living Room", "rssi_threshold": -70, "last_seen": None},
    "esp32_node_2": {"name": "Bedroom", "rssi_threshold": -70, "last_seen": None}
}

users = {
    "Taavi": {"devices": [{"id":"SM-G986B","name":"Telefon"}, {"id":"KT-001","name":"Nutikell"}]},
    "Juku": {"devices": [{"id":"SM-F731B","name":"Telefon"}]}
}

# MQTT loop in background
def mqtt_loop():
    import paho.mqtt.client as mqtt
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

# --- Flask routes ---
@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/heartbeat/<device_id>", methods=["POST"])
def heartbeat(device_id):
    if device_id in devices:
        devices[device_id]["last_seen"] = "now"
        return jsonify({"status": "ok"})
    return jsonify({"error": "Unknown device"}), 404

@app.route("/devices/<device_id>", methods=["POST"])
def update_device(device_id):
    data = request.json
    if device_id not in devices:
        return jsonify({"error": "Unknown device"}), 404
    for key in ["name", "rssi_threshold"]:
        if key in data:
            devices[device_id][key] = data[key]
    return jsonify(devices[device_id])

@app.route("/users/<user_name>/devices", methods=["POST"])
def add_user_device(user_name):
    data = request.json
    if user_name not in users:
        users[user_name] = {"devices": []}
    users[user_name]["devices"].append(data)
    return jsonify(users[user_name])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
