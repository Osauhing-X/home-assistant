ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Paigalda kõik vajalikud paketid
RUN apk add --no-cache \
    python3 \
    py3-flask \
    py3-paho-mqtt \
    lighttpd

# Kopeeri skriptid ja front-end
COPY run.sh /run.sh
COPY webui.py /data/webui.py
COPY server.py /data/server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
