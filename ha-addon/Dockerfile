ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda lighttpd ja python3 + virtuaalkeskkonna tugi
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    lighttpd \
    curl

# Kopeeri skriptid ja front-end
COPY www /www
COPY server.py /server.py
COPY run.sh /run.sh


RUN chmod +x /run.sh /server.py

# Python virtual environment + paketid build time'is
RUN python3 -m venv /venv \
 && . /venv/bin/activate \
 && pip install --no-cache-dir --upgrade pip \
 && pip install flask paho-mqtt

CMD [ "/run.sh" ]
