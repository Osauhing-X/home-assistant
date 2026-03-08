ARG BUILD_FROM
FROM $BUILD_FROM

# For WWW folder
RUN apk add --no-cache lighttpd

COPY run.sh /run.sh
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
