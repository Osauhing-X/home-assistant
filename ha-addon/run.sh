#!/usr/bin/with-contenv bashio
# -------------------------------------------------------------------
# ESP32 BLE Presence Addon
# Käivitab Flask serveri ja Lighttpd front-endi jaoks
# -------------------------------------------------------------------

echo "Starting ESP32 BLE Presence Addon..."

# Kontrollime, et Python3 ja pip3 oleks olemas
if ! command -v python3 >/dev/null 2>&1; then
    echo "Installing python3 + pip3..."
    apk add --no-cache python3 py3-pip
fi

# Install Flask ja MQTT ainult, kui pole
if ! python3 -c "import flask" >/dev/null 2>&1; then
    echo "Installing Flask and paho-mqtt..."
    pip3 install --no-cache-dir flask paho-mqtt
fi

# Käivitame Flask serveri backgroundis
echo "Starting Flask server..."
python3 /data/server.py &

# Käivitame Lighttpd UI ingressi
echo "Starting Lighttpd ingress UI..."
python3 /data/webui.py
