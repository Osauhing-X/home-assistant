#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Addon WebUI..."

# Käivita Lighttpd
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

# Veebiliides
lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Käivita virtualenv
. /opt/venv/bin/activate

# Käivita Flask ja MQTT serverid eraldi
python3 /server/mqtt_server.py &
python3 /server/flask_app.py &

wait
