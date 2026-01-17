from flask import Flask, jsonify, request
import threading
import time
import os
import uuid

app = Flask(__name__)

# --- Andmete struktuur ---
users = [
    {"unique_id": "user_1", "user_name": "Tom"},
    {"unique_id": "user_2", "user_name": "Juku"}
]

devices = [
    {"unique_id": "dev_1", "custom_name": "Telefon Tom", "USER_ID": "user_1", "in_room": None},
    {"unique_id": "dev_2", "custom_name": "Nutikell Tom", "USER_ID": "user_1", "in_room": None},
    {"unique_id": "dev_3", "custom_name": "Telefon Juku", "USER_ID": "user_2", "in_room": None}
]

rooms = [
    {"HA_register_room_id": "room_1", "HA_register_room_name": "Elutuba"},
    {"HA_register_room_id": "room_2", "HA_register_room_name": "Magamistuba"}
]

esp32 = [
    {"unique_id": "esp32_1", "custom_name": "ESP32 Node 1", "ROOM_ID": None},
    {"unique_id": "esp32_2", "custom_name": "ESP32 Node 2", "ROOM_ID": None}
]

# --- Utils ---
def find_index(arr, key, value):
    for idx, item in enumerate(arr):
        if item.get(key) == value:
            return idx
    return -1

# --- MQTT loop (BLE node simulator) ---
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

# --- API ---
@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rooms)

@app.route("/api/esp32", methods=["GET"])
def get_esp32():
    return jsonify(esp32)

# Lisamine
@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.json
    new_user = {
        "unique_id": str(uuid.uuid4()),
        "user_name": data.get("user_name")
    }
    users.append(new_user)
    return jsonify(new_user)

@app.route("/api/rooms", methods=["POST"])
def add_room():
    data = request.json
    new_room = {
        "HA_register_room_id": str(uuid.uuid4()),
        "HA_register_room_name": data.get("room_name")
    }
    rooms.append(new_room)
    return jsonify(new_room)

# --- Update device in_room ---
@app.route("/api/devices/<device_id>", methods=["POST"])
def update_device(device_id):
    idx = find_index(devices, "unique_id", device_id)
    if idx == -1:
        return jsonify({"error": "unknown device"}), 404
    devices[idx].update(request.json)  # siia saab in_room
    return jsonify(devices[idx])

# --- Update ESP32 ROOM_ID ---
@app.route("/api/esp32/<esp_id>", methods=["POST"])
def update_esp32(esp_id):
    idx = find_index(esp32, "unique_id", esp_id)
    if idx == -1:
        return jsonify({"error": "unknown ESP32"}), 404
    esp32[idx].update(request.json)  # siia ROOM_ID
    return jsonify(esp32[idx])

# --- Kustuta ---
@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    idx = find_index(users, "unique_id", user_id)
    if idx == -1:
        return jsonify({"error": "unknown user"}), 404
    users.pop(idx)
    return jsonify({"status": "ok"})

@app.route("/api/rooms/<room_id>", methods=["DELETE"])
def delete_room(room_id):
    idx = find_index(rooms, "HA_register_room_id", room_id)
    if idx == -1:
        return jsonify({"error": "unknown room"}), 404
    rooms.pop(idx)
    return jsonify({"status": "ok"})

# --- Run server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
