ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python sõltuvused, kui vaja
RUN pip install --no-cache-dir flask paho-mqtt

# Copy addon files
COPY run.sh /
COPY www /data/www
RUN chmod +x /run.sh

# Expose webserver port
EXPOSE 5000

# Entrypoint
CMD [ "/run.sh" ]
