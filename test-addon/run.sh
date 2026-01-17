#!/usr/bin/with-contenv bashio

echo "Starting Lighttpd ingress UI on port 8099"

lighttpd -D -f /etc/lighttpd/lighttpd.conf
