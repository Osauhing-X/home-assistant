ARG BUILD_FROM
FROM $BUILD_FROM

# Node.js ja git
RUN apk add --no-cache nodejs npm git

# Build-time kloon priv repo /app
ARG REPO
ARG TOKEN
RUN git clone https://$TOKEN@github.com/$REPO /app

WORKDIR /app
RUN npm install --omit=dev

# run.sh rootis, PID 1 foreground
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]