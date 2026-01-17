# Näidisandmed
users = [
    {"unique_id": "u1", "user_name": "Alice"},
    {"unique_id": "u2", "user_name": "Bob"}
]

devices = [
    {"unique_id": "d1", "custom_name": "ESP32-A", "USER_ID": "u1", "in_room": None},
    {"unique_id": "d2", "custom_name": "ESP32-B", "USER_ID": "u2", "in_room": None}
]

rooms = [
    {"HA_register_room_id": "r1", "HA_register_room_name": "Tuba 1"},
    {"HA_register_room_id": "r2", "HA_register_room_name": "Tuba 2"}
]

esp32_nodes = [
    {"unique_id": "n1", "custom_name": "ESP32 Node A", "ROOM_ID": None},
    {"unique_id": "n2", "custom_name": "ESP32 Node B", "ROOM_ID": None}
]
