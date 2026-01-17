#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Addon WebUI..."

# Käivita Lighttpd koos Flask proxyga
cat <<EOF >/etc/lighttpd/lighttpd.conf
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog", "mod_proxy")
$HTTP["url"] =~ "^/api/" {
    proxy.server  = ( "" => ( "host" => "127.0.0.1", "port" => 5000 ) )
}
index-file.names = ("index.html")
EOF

lighttpd -D -f /etc/lighttpd/lighttpd.conf &

# Aktiveeri virtualenv
. /opt/venv/bin/activate

# Käivita Flask ja MQTT serverid
python3 /server/mqtt.py &
python3 /server/flask_app.py &

wait
