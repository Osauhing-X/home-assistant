#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

# Aktiveeri Python virtual environment
. /venv/bin/activate

# Käivitame Flask serveri taustas
echo "Starting Flask server..."
python3 /server.py &

# Lighttpd konfiguratsioon
echo "Configuring Lighttpd..."
mkdir -p /var/www/localhost/htdocs
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"
EOF

# Kopeeri front-end failid
if [ -d "/www" ]; then
    cp -r /www/* /var/www/localhost/htdocs/
else
    echo "Warning: /www folder missing!"
fi

# Käivitame Lighttpd foregroundis
echo "Starting Lighttpd ingress UI..."
exec lighttpd -D -f /etc/lighttpd/lighttpd.conf
