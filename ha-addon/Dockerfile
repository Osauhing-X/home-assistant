ARG BUILD_FROM
FROM $BUILD_FROM

# Python + deps
RUN apk add --no-cache python3 py3-pip \
    && pip3 install --no-cache-dir flask paho-mqtt

COPY run.sh /run.sh
COPY app.py /app.py
COPY www /www

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
