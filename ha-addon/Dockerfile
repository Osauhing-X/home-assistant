ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda Python + venv + pip
RUN apk add --no-cache python3 py3-venv py3-pip

# Paigalda lighttpd (optionaalne staatiliste failide jaoks)
RUN apk add --no-cache lighttpd

# Kopeeri addon failid
COPY run.sh /run.sh
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

# Käivita run.sh
CMD [ "/run.sh" ]
