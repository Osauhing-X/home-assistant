FROM alpine:3.21

# Install Python + pip + bash + lighttpd
RUN apk add --no-cache python3 py3-pip py3-virtualenv bash lighttpd curl

# Loo virtualenv
RUN python3 -m virtualenv /opt/venv

# Install Flask ja paho-mqtt virtualenv-i sisse
RUN /opt/venv/bin/pip install --no-cache-dir flask paho-mqtt

# Copy veeb ja server
COPY www /var/www/localhost/htdocs
COPY server /server
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
