#!/usr/bin/with-contenv bashio

echo "Starting ESP32 BLE Presence Test Addon..."

python3 - <<'EOF'
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="/data/www")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
