ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda lighttpd ja python3 + virtuaalkeskkonna tugi
RUN apk add --no-cache lighttpd python3 py3-pip bash

# Kopeeri skriptid ja front-end
COPY run.sh /run.sh
COPY webui.py /webui.py
COPY server.py /server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
