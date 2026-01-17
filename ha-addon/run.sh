#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

# Activate Python virtual environment
. /venv/bin/activate

# Start Flask server in background
echo "Starting Flask server..."
python3 /server.py &

# Configure Lighttpd for SPA fallback
echo "Configuring Lighttpd..."
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog", "mod_rewrite")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"

# SPA fallback: all unknown paths go to index.html
url.rewrite-if-not-file = (
    ".*" => "/index.html"
)
EOF

# Start Lighttpd in foreground
echo "Starting Lighttpd ingress UI..."
lighttpd -D -f /etc/lighttpd/lighttpd.conf
