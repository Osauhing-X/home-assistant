#!/usr/bin/with-contenv bashio
echo "---"

set -e

# Ingress port
HTTP=${HTTP:-8100}

echo "Starting ESP32 BLE Addon WebUI on port $HTTP..."

# Lighttpd config
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = $HTTP
server.bind = "0.0.0.0"

server.modules += ("mod_proxy")
\$HTTP["url"] =~ "^/api/" {
    proxy.server = ( "" => (("host" => "127.0.0.1", "port" => 5000)) )
}

server.document-root = "/var/www/localhost/htdocs"
server.modules += ("mod_accesslog")
index-file.names = ("index.html")
EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Flask server
python3 /server/flask_app.py

wait
