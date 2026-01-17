ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Paigalda lighttpd ja Python (ainult pip3 + python3)
RUN apk add --no-cache lighttpd python3 py3-pip

# Kopeeri addon failid
COPY run.sh /run.sh
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
