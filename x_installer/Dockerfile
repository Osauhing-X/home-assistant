ARG BUILD_FROM
FROM $BUILD_FROM

# Installer requirements
RUN apk add --no-cache git jq bash

# Kopeeri skriptid
COPY run.sh /run.sh
COPY apply_updates.sh /apply_updates.sh

# Tee täidetavaks
RUN chmod +x /run.sh /apply_updates.sh

CMD [ "/run.sh" ]