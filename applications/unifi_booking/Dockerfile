ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.21
FROM ${BUILD_FROM}
RUN apk add --no-cache nodejs
WORKDIR /app
COPY package.json ./
COPY src ./src
COPY public ./public
CMD ["node", "src/server.js"]
