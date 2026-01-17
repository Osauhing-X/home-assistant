#!/usr/bin/with-contenv bashio

echo "Starting ESP32 BLE Addon WebUI..."

# Käivita MQTT taustal
python3 /server/mqtt.py &

# Käivita Flask API taustal
python3 /server/flask.py &

# Lighttpd veebiliides foregroundis
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf
