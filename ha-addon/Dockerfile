ARG BUILD_FROM=alpine:3.21
FROM $BUILD_FROM

# Paigalda vajalikud paketid
RUN apk add --no-cache python3 py3-pip py3-virtualenv bash lighttpd curl

# Loo virtualenv
RUN python3 -m virtualenv /opt/venv

# Install Flask ja MQTT virtualenv-i sisse
RUN /opt/venv/bin/pip install --no-cache-dir flask paho-mqtt

# Kopeeri WebUI ja serveri failid
COPY www /var/www/localhost/htdocs
COPY server /server
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
