ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

RUN apk add --no-cache \
    python3 \
    py3-flask \
    lighttpd \
    bash

COPY run.sh /run.sh
COPY server /server
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
