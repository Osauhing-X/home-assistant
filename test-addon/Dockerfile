# Base image with Python
FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir flask paho-mqtt

# Copy addon files
COPY run.sh /run.sh
COPY www /data/www
RUN chmod +x /run.sh

# Expose webserver port
EXPOSE 5000

# Entrypoint
CMD ["/run.sh"]
