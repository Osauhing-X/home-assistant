ARG BUILD_FROM
FROM $BUILD_FROM

# Install venv
RUN apk add --no-cache python3 py3-venv

# Create virtual environment ja installi sinna vajalikud paketid
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --no-cache-dir flask paho-mqtt

# Copy addon files
COPY run.sh /
COPY www /data/www
RUN chmod +x /run.sh

EXPOSE 5000
CMD [ "/run.sh" ]
