#!/usr/bin/with-contenv bashio
# -------------------------------------------------------------------
# ESP32 BLE Presence Addon
# Käivitab Flask serveri ja Lighttpd front-endi
# -------------------------------------------------------------------

echo "Starting ESP32 BLE Presence Addon..."

# Loo Python virtuaalkeskkond, kui seda pole
if [ ! -d "/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv /venv
fi

# Activate virtuaalkeskkond
. /venv/bin/activate

# Install Flask ja MQTT, kui neid pole
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir flask paho-mqtt

# Käivitame Flask serveri backgroundis
echo "Starting Flask server..."
python /server.py &

# Käivitame Lighttpd front-end UI
echo "Starting Lighttpd ingress UI..."
python /webui.py
