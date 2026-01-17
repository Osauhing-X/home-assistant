ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip bash lighttpd curl

COPY run.sh /run.sh
RUN chmod +x /run.sh

COPY www /var/www/localhost/htdocs
COPY server /server

CMD [ "/run.sh" ]
