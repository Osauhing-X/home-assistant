ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache bash git curl python3 py3-pip unzip

COPY run.sh /run.sh
COPY installer.py /app/installer.py
RUN chmod +x /run.sh

CMD [ "/run.sh" ]