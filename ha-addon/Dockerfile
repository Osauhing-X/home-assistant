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
COPY run.sh /run.sh
COPY webui.py /webui.py
COPY server.py /server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh /server.py /webui.py

# Python virtual environment + paketid build time'is
RUN python3 -m venv /venv \
 && . /venv/bin/activate \
 && pip install --no-cache-dir --upgrade pip \
 && pip install flask paho-mqtt

CMD [ "/run.sh" ]
