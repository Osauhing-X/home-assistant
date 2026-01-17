ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda lighttpd
RUN apk add --no-cache lighttpd

COPY run.sh /run.sh
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
