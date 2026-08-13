ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 PORT=3000 DATA_DIR=/data

RUN apk add --no-cache nodejs npm git jq bash ffmpeg

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --include=dev
COPY . .
RUN npm run build \
    && npm prune --omit=dev --ignore-scripts \
    && chmod +x /app/run.sh

ENV NODE_ENV=production

CMD ["/app/run.sh"]
