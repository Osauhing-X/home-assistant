ARG BUILD_FROM
FROM $BUILD_FROM

# Install git Node.js jaoks
RUN apk add --no-cache nodejs npm git

# run.sh rootis
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]