#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

# Aktiveeri virtual environment
. /venv/bin/activate

# Käivitame Flask serveri taustas
echo "Starting Flask server..."
python3 /server.py &

# Käivitame Lighttpd foregroundis
echo "Starting Lighttpd ingress UI..."
python3 /webui.py
