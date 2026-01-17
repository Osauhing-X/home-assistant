#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

# Käivitame Flask API taustas
. /venv/bin/activate
echo "Starting Flask server..."
python3 /server.py &

# Konfigureerime Lighttpd front-end
echo "Configuring Lighttpd..."
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"
EOF

echo "Starting Lighttpd ingress UI..."
lighttpd -D -f /etc/lighttpd/lighttpd.conf
