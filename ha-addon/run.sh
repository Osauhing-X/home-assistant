#!/usr/bin/with-contenv bashio
echo "---"

set -e

HTTP=${HTTP:-8099}

echo "Starting ESP32 BLE Addon WebUI on port $HTTP..."

# Lighttpd config
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = $HTTP
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Flask server
[ -f /server/flask_app.py ] && python3 /server/flask_app.py &

# MQTT server
[ -f /server/mqtt.py ] && python3 /server/mqtt.py &

wait
