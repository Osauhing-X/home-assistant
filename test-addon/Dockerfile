# Home Assistant addoni baas
ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python ja pip
RUN apk add --no-cache python3 py3-pip

# Install Flask
RUN pip3 install --no-cache-dir flask

# Copy addon files
COPY run.sh /run.sh
COPY www /data/www
RUN chmod a+x /run.sh

# Expose port (HA ingress ei kasuta tegelikult seda)
EXPOSE 5000

# Käivita addon
CMD [ "/run.sh" ]
