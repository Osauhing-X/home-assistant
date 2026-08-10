ARG BUILD_ARCH=amd64
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base:latest

# Installer requirements
RUN apk add --no-cache git jq bash

# Kopeeri skriptid
COPY run.sh /run.sh

# Tee täidetavaks
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
