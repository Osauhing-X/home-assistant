from flask import Flask, jsonify, request
import threading
import time

app = Flask(__name__)

# AJUTISED mälus olevad andmed
rooms = {}  # {room_id: {"name": room_name}}
users = {}  # {user_id: {"name": user_name, "devices":[device_ids]}}
devices = {} # {device_id: {"custom_name": name, "user_id": uid, "in_room": room_id}}
esp32_nodes = {}  # {esp32_id: {"custom_name": name, "room_id": room_id}}

@app.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify([{"id": rid, "name": r["name"]} for rid, r in rooms.items()])

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify([{"id": uid, "name": u["name"]} for uid, u in users.items()])

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify([{"id": did, **d} for did, d in devices.items()])

@app.route("/esp32", methods=["GET"])
def get_esp32():
    return jsonify([{"id": eid, **e} for eid, e in esp32_nodes.items()])

@app.route("/rooms", methods=["POST"])
def add_room():
    data = request.json
    room_id = data.get("id")
    room_name = data.get("name")
    if not room_id or not room_name:
        return jsonify({"error": "id and name required"}), 400
    rooms[room_id] = {"name": room_name}
    return jsonify(rooms[room_id])

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    user_id = data.get("id")
    user_name = data.get("name")
    if not user_id or not user_name:
        return jsonify({"error": "id and name required"}), 400
    users[user_id] = {"name": user_name, "devices": []}
    return jsonify(users[user_id])

@app.route("/devices", methods=["POST"])
def add_device():
    data = request.json
    device_id = data.get("id")
    if not device_id:
        return jsonify({"error": "id required"}), 400
    devices[device_id] = {
        "custom_name": data.get("custom_name", ""),
        "user_id": data.get("user_id"),
        "in_room": data.get("in_room")
    }
    # Lisa seadme kasutajale
    uid = data.get("user_id")
    if uid in users:
        users[uid]["devices"].append(device_id)
    return jsonify(devices[device_id])

@app.route("/esp32", methods=["POST"])
def add_esp32():
    data = request.json
    esp_id = data.get("id")
    if not esp_id:
        return jsonify({"error": "id required"}), 400
    esp32_nodes[esp_id] = {
        "custom_name": data.get("custom_name", ""),
        "room_id": data.get("room_id")
    }
    return jsonify(esp32_nodes[esp_id])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
