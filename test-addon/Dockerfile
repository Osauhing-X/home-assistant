ARG BUILD_FROM
FROM $BUILD_FROM

# Copy addon files
COPY run.sh /
COPY www /data/www
RUN chmod +x /run.sh

EXPOSE 5000
CMD [ "/run.sh" ]
