from flask import Flask, jsonify, request
from data import users, devices, rooms, esp32_nodes

app = Flask(__name__)

# --- GET endpoints ---
@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rooms)

@app.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices + esp32_nodes)

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

# --- POST endpoints ---
@app.route("/api/rooms", methods=["POST"])
def add_room():
    data = request.json
    if not data or "HA_register_room_id" not in data:
        return jsonify({"error": "Missing room id"}), 400
    rooms.append({
        "HA_register_room_id": data["HA_register_room_id"],
        "HA_register_room_name": data.get("HA_register_room_name", "Uus Tuba")
    })
    return jsonify({"success": True})

@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.json
    if not data or "unique_id" not in data:
        return jsonify({"error": "Missing user id"}), 400
    users.append({
        "unique_id": data["unique_id"],
        "user_name": data.get("user_name", "Uus Kasutaja")
    })
    return jsonify({"success": True})

@app.route("/api/devices/<device_id>/assign_room", methods=["POST"])
def assign_device_to_room(device_id):
    data = request.json
    room_id = data.get("room_id")
    if not room_id:
        return jsonify({"error": "Missing room_id"}), 400
    for dev in devices + esp32_nodes:
        if dev["unique_id"] == device_id:
            dev["in_room"] = room_id
            return jsonify({"success": True})
    return jsonify({"error": "Device not found"}), 404

if __name__ == "__main__":
    import paho.mqtt.client as mqtt
    client = mqtt.Client(client_id="", protocol=mqtt.MQTTv311)
    # siia saab lisada mqtt callbackid, kui vaja
    app.run(host="0.0.0.0", port=5000)
