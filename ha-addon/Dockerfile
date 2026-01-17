# Build arg HA Supervisor poolt
ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python ja vajalikud paketid
# HA base image’is on tavaliselt Python juba olemas, aga vajadusel saab lisada pip paketid
RUN pip install --no-cache-dir flask paho-mqtt

# Kopeeri addon failid
COPY run.sh /
COPY www /data/www

# Tee run.sh täidetavaks
RUN chmod a+x /run.sh

# Ava port webui jaoks (ingress)
EXPOSE 5000

# Käivita addon
CMD [ "/run.sh" ]
