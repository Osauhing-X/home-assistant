#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Addon WebUI..."

# Start Lighttpd
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Activate Python virtualenv
. /opt/venv/bin/activate

# Start serverid
python3 /server/mqtt.py &
python3 /server/flask_app.py &

wait
