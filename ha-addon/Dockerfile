ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache python3 bash lighttpd curl

# Setup Python virtual environment
RUN python3 -m ensurepip \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install flask paho-mqtt

# Copy files
COPY www /var/www/localhost/htdocs
COPY server /server
COPY run.sh /run.sh

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
