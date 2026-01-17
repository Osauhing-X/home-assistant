ARG BUILD_FROM
FROM $BUILD_FROM

# Lisa vajalikud paketid
RUN apk add --no-cache python3 py3-pip python3-venv lighttpd

# Tee virtualenv
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install Flask paho-mqtt

# Kopeeri kood
COPY run.sh /run.sh
COPY server /server
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
