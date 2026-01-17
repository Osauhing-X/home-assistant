#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

# Käivitame Flask taustas
. /venv/bin/activate
python3 /server.py &

# Konfigureerime Lighttpd
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"
EOF

echo "Starting Lighttpd..."
lighttpd -D -f /etc/lighttpd/lighttpd.conf
