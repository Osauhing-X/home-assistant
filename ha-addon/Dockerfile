ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda lighttpd ja python
RUN apk add --no-cache lighttpd python3 py3-pip

# Paigalda Flask
RUN pip3 install Flask paho-mqtt

COPY run.sh /run.sh
COPY server /server
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
