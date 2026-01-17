#!/usr/bin/with-contenv bashio
echo "Starting ESP32 BLE Presence Addon..."

# Käivitame Flask serveri
echo "Starting Flask server..."
python3 /server.py &

# Käivitame Lighttpd front-endi
echo "Starting Lighttpd ingress UI..."
python3 /webui.py
