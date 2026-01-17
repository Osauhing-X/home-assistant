FROM alpine:3.21

# --- Base dependencies ---
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    lighttpd \
    curl

WORKDIR /data

# Kopeeri kõik failid addonisse
COPY run.sh /run.sh
COPY server.py /server.py
COPY webui.py /webui.py
COPY www /www

RUN chmod +x /run.sh /server.py /webui.py

# Python virtual environment + paketid build time'is
RUN python3 -m venv /venv \
 && . /venv/bin/activate \
 && pip install --no-cache-dir --upgrade pip \
 && pip install flask paho-mqtt

CMD ["/run.sh"]
