ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Install Python3 + Flask + MQTT + Lighttpd
RUN apk add --no-cache python3 py3-flask py3-paho-mqtt lighttpd

# Copy addon files
COPY run.sh /run.sh
COPY server.py /server.py
COPY webui.py /webui.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
