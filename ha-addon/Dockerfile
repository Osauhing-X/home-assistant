ARG BUILD_FROM=ghcr.io/home-assistant/base:3.19
FROM ${BUILD_FROM}

# Environment
ENV LANG C.UTF-8

# System dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    lighttpd \
    bash

# Python dependencies
RUN pip3 install --no-cache-dir flask

# Copy addon files
COPY run.sh /run.sh
COPY server /server
COPY www /var/www/localhost/htdocs

# Permissions
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
