#!/usr/bin/with-contenv bashio
set -e

# defineeri port
HTTP=${HTTP:-8099}

echo "Starting ESP32 BLE Addon WebUI on port $HTTP..."

# Lighttpd konfiguratsioon
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = $HTTP
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
EOF

# Käivita Lighttpd taustal
lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# aktiveeri Python virtualenv
. /opt/venv/bin/activate

# Käivita serverid, kui failid olemas
[ -f /server/mqtt.py ] && python3 /server/mqtt.py &
[ -f /server/flask_app.py ] && python3 /server/flask_app.py &

wait
