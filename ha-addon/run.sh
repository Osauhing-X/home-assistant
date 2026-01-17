#!/usr/bin/with-contenv bashio
set -e

HTTP=${HTTP:-8099}  # vaikimisi port 8099

echo "Starting ESP32 BLE Addon WebUI on port $HTTP..."

# Lighttpd konfiguratsioon
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = $HTTP
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

# Käivita Lighttpd
lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Active Python virtualenv
. /opt/venv/bin/activate

# Käivita serverid
python3 /server/mqtt.py &
python3 /server/flask_app.py &

wait
