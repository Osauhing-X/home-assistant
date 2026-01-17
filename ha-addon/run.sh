#!/usr/bin/with-contenv bashio
echo "---"

# =============================================================================
# run.sh - ESP32 BLE Addon WebUI
# =============================================================================

# Failide õigused
bashio::log.info "Fixing permissions..."
chown -R root:root /server /var/www/localhost/htdocs

# Käivita lighttpd
bashio::log.info "Starting lighttpd..."
lighttpd -f /etc/lighttpd/lighttpd.conf

# Virtual environment path
VENV_PATH="/opt/venv"

# Kui venv ei eksisteeri, loo see
if [ ! -d "$VENV_PATH" ]; then
    bashio::log.info "Creating Python virtual environment..."
    python3 -m venv $VENV_PATH
fi

# Aktiviseeri venv
source $VENV_PATH/bin/activate

# Paigalda Flask ja MQTT ainult venv-sse
bashio::log.info "Installing Python dependencies..."
pip install --upgrade pip
pip install Flask paho-mqtt

# Käivita Flask rakendus
bashio::log.info "Starting ESP32 BLE Addon WebUI..."
export FLASK_APP=/server/flask_app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

# Flask logib konsooli
flask run
