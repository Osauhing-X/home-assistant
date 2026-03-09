ARG BUILD_FROM
FROM $BUILD_FROM

# Node.js ja git
RUN apk add --no-cache nodejs npm git

# run.sh rootis, PID 1 foreground
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]