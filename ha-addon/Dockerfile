ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    lighttpd \
    curl \
    && python3 -m venv /venv

# Copy addon scripts & front-end
COPY run.sh /run.sh
COPY server.py /server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh /server.py

# Install Python packages inside venv
RUN . /venv/bin/activate \
    && pip install --no-cache-dir flask paho-mqtt

CMD ["/run.sh"]
