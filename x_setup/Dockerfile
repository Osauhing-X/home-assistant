ARG BUILD_FROM
FROM $BUILD_FROM

# Install Node.js
RUN apk add --no-cache nodejs npm

# Kopeeri Node.js rakendus
COPY index.js /app/index.js
COPY plugins /app/plugins

WORKDIR /app

CMD ["node", "index.js"]