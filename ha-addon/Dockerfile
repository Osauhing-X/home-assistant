ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    lighttpd \
    curl \
    && python3 -m ensurepip \
    && pip install --no-cache-dir --upgrade pip

# Copy scripts and front-end
COPY run.sh /run.sh
COPY server.py /server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh /server.py

# Create Python venv and install Python packages
RUN python3 -m venv /venv \
 && . /venv/bin/activate \
 && pip install --no-cache-dir flask paho-mqtt

CMD ["/run.sh"]
