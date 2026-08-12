ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 NODE_ENV=production PORT=3000 DATA_DIR=/data

RUN apk add --no-cache nodejs npm git jq bash

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build && chmod +x /run.sh

CMD ["/run.sh"]

