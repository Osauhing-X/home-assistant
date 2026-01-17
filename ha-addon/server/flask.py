from flask import Flask, jsonify
from mqtt import ble_devices

app = Flask(__name__)

@app.route("/api/devices")
def get_devices():
    return jsonify(ble_devices)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
