from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Andmehoidla ---
users = [
    # { "unique_id": "u1", "user_name": "Mari" }
]

devices = [
    # { "unique_id": "d1", "custom_name": "ESP32 Hall", "user_id": "u1", "in_room": "r1" }
]

rooms = [
    # { "HA_register_room_id": "r1", "HA_register_room_name": "Eesruum" }
]

esp32_nodes = [
    # { "unique_id": "n1", "custom_name": "Node A", "room_id": "r1" }
]

# --- UTILITY ---
def find_item(collection, key, value):
    return next((item for item in collection if item.get(key) == value), None)

def remove_item(collection, key, value):
    collection[:] = [item for item in collection if item.get(key) != value]

# --- ROOMS ---
@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rooms)

@app.route("/api/rooms", methods=["POST"])
def add_room():
    data = request.json
    if not data.get("HA_register_room_id") or not data.get("HA_register_room_name"):
        return jsonify({"error": "Invalid data"}), 400
    if find_item(rooms, "HA_register_room_id", data["HA_register_room_id"]):
        return jsonify({"error": "Room already exists"}), 400
    rooms.append(data)
    return jsonify(data), 201

@app.route("/api/rooms/<room_id>", methods=["DELETE"])
def delete_room(room_id):
    remove_item(rooms, "HA_register_room_id", room_id)
    # Update devices / nodes
    for d in devices:
        if d.get("in_room") == room_id:
            d["in_room"] = None
    for n in esp32_nodes:
        if n.get("room_id") == room_id:
            n["room_id"] = None
    return jsonify({"deleted": room_id})

# --- USERS ---
@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.json
    if not data.get("unique_id") or not data.get("user_name"):
        return jsonify({"error": "Invalid data"}), 400
    if find_item(users, "unique_id", data["unique_id"]):
        return jsonify({"error": "User already exists"}), 400
    users.append(data)
    return jsonify(data), 201

@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    remove_item(users, "unique_id", user_id)
    for d in devices:
        if d.get("user_id") == user_id:
            d["user_id"] = None
    return jsonify({"deleted": user_id})

# --- DEVICES ---
@app.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/api/devices", methods=["POST"])
def add_device():
    data = request.json
    if not data.get("unique_id") or not data.get("custom_name"):
        return jsonify({"error": "Invalid data"}), 400
    if find_item(devices, "unique_id", data["unique_id"]):
        return jsonify({"error": "Device already exists"}), 400
    devices.append(data)
    return jsonify(data), 201

@app.route("/api/devices/<device_id>", methods=["DELETE"])
def delete_device(device_id):
    remove_item(devices, "unique_id", device_id)
    return jsonify({"deleted": device_id})

# --- ESP32 NODES ---
@app.route("/api/nodes", methods=["GET"])
def get_nodes():
    return jsonify(esp32_nodes)

@app.route("/api/nodes", methods=["POST"])
def add_node():
    data = request.json
    if not data.get("unique_id") or not data.get("custom_name"):
        return jsonify({"error": "Invalid data"}), 400
    if find_item(esp32_nodes, "unique_id", data["unique_id"]):
        return jsonify({"error": "Node already exists"}), 400
    esp32_nodes.append(data)
    return jsonify(data), 201

@app.route("/api/nodes/<node_id>", methods=["DELETE"])
def delete_node(node_id):
    remove_item(esp32_nodes, "unique_id", node_id)
    return jsonify({"deleted": node_id})

# --- RUN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
