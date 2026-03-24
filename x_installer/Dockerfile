ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda vajalikud süsteemi paketid
RUN apk add --no-cache bash git curl python3 py3-pip unzip

# Paigalda Python moodulid
RUN pip install --no-cache-dir requests

COPY run.sh /run.sh
COPY installer.py /app/installer.py
RUN chmod +x /run.sh

CMD [ "/run.sh" ]