ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda lighttpd + curl (vajadusel)
RUN apk add --no-cache lighttpd curl

# Kopeeri käivitusskript + www kaust
COPY run.sh /run.sh
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

# Käivita s6 teenus
CMD [ "/run.sh" ]
