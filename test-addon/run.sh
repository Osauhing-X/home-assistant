#!/usr/bin/with-contenv bashio
# Fail peab olema executable

# Loo virtuaalkeskkond Python paketitele
python3 -m venv /venv
. /venv/bin/activate

# Install vajalikud paketid venv-i
pip install --no-cache-dir flask paho-mqtt

# Käivita Flask
cd /data/www
python -m flask run --host=0.0.0.0 --port=5000
