ARG BUILD_ARCH=amd64
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base:latest

# Node.js ja git
RUN apk add --no-cache nodejs npm git

# run.sh rootis, PID 1 foreground
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
