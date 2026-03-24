ARG BUILD_FROM
FROM $BUILD_FROM

# Installer requirements
RUN apk add --no-cache bash git curl unzip jq

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]