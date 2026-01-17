ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip bash lighttpd

# Kopeeri run.sh ja front-end
COPY run.sh /run.sh
COPY server.py /server.py
COPY www /var/www/localhost/htdocs

RUN chmod +x /run.sh /server.py

# Virtual environment Pythonile
RUN python3 -m venv /venv \
 && . /venv/bin/activate \
 && pip install --no-cache-dir --upgrade pip \
 && pip install flask paho-mqtt

CMD [ "/run.sh" ]
