ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python, pip, Lighttpd
RUN apk add --no-cache python3 py3-pip lighttpd bash

# Kopeeri failid
COPY run.sh /run.sh
COPY server.py /server.py
COPY webui.py /webui.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh

# Set entrypoint
CMD [ "/run.sh" ]
