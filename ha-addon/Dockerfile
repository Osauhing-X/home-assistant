ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Lisa vajalikud paketid
RUN apk add --no-cache python3 py3-pip lighttpd bash

# Tee virtualenv otse
RUN python3 -m venv /opt/venv

# Kopeeri serveri failid
COPY server /server
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Addon entrypoint
CMD [ "/run.sh" ]
