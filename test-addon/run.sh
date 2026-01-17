#!/usr/bin/with-contenv bashio

echo "Starting static file UI..."

# Lihtne CLI-põhine server staatiliste failide serveerimiseks
# Kasutame s6-s oleva `httpd` võimalust
# /data/www kaustast serveeritakse index.html ja logo.png

httpd -p 8099 -h /data/www
