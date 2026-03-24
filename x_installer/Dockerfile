ARG BUILD_FROM
FROM $BUILD_FROM

# Paigalda vajalikud süsteemi paketid + Python moodulid
RUN apk add --no-cache bash git curl python3 py3-pip unzip py3-requests

COPY run.sh /run.sh
COPY installer.py /app/installer.py
RUN chmod +x /run.sh

CMD [ "/run.sh" ]