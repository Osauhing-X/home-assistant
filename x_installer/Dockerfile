ARG BUILD_FROM
FROM $BUILD_FROM

# Installer requirements
RUN apk add --no-cache git jq bash

# Kopeeri skriptid
COPY run.sh /run.sh

# Tee täidetavaks
RUN chmod +x /run.sh

CMD [ "/run.sh" ]