ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python3 ja pip (HA minimal image’il)
RUN apk add --no-cache python3 py3-pip

# Install Python paketid
RUN pip3 install --no-cache-dir flask paho-mqtt

# Copy addon files
COPY run.sh /
COPY www /data/www
RUN chmod a+x /run.sh

EXPOSE 5000

CMD [ "/run.sh" ]
