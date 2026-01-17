#!/usr/bin/with-contenv bashio
# -------------------------------------------------------------------
# ESP32 BLE Presence Addon
# Käivitab Flask serveri ja Lighttpd UI
# -------------------------------------------------------------------

echo "Starting ESP32 BLE Presence Addon..."

# Kontrollime Python3 + pip3 olemasolu
if ! command -v python3 >/dev/null 2>&1; then
    echo "Installing python3 + pip3..."
    apk add --no-cache python3 py3-pip
fi

# Loo virtuaalne keskkond Python paketide jaoks
if [ ! -d "/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv /venv
fi
. /venv/bin/activate

# Install Flask ja MQTT ainult virtuaalkeskkonda
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir flask paho-mqtt

# Käivitame Flask serveri backgroundis
echo "Starting Flask server..."
python3 /server.py &

# Käivitame Lighttpd ingress UI
echo "Starting Lighttpd ingress UI..."
python3 /webui.py
