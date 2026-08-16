ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 PORT=3000 DATA_DIR=/data

RUN apk add --no-cache nodejs npm git jq bash ffmpeg iproute2

ARG MEDIAMTX_VERSION=1.19.3
RUN MTX_ARCH="$(apk --print-arch)" \
    && case "$MTX_ARCH" in x86_64) MTX_ARCH=amd64 ;; aarch64) MTX_ARCH=arm64 ;; armv7) MTX_ARCH=armv7 ;; *) echo "Unsupported MediaMTX architecture: $MTX_ARCH"; exit 1 ;; esac \
    && wget -q "https://github.com/bluenviron/mediamtx/releases/download/v${MEDIAMTX_VERSION}/mediamtx_v${MEDIAMTX_VERSION}_linux_${MTX_ARCH}.tar.gz" -O /tmp/mediamtx.tar.gz \
    && tar -xzf /tmp/mediamtx.tar.gz -C /usr/local/bin mediamtx \
    && chmod +x /usr/local/bin/mediamtx \
    && rm /tmp/mediamtx.tar.gz

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --include=dev
COPY . .
RUN npm run build \
    && npm prune --omit=dev --ignore-scripts \
    && chmod +x /app/run.sh

ENV NODE_ENV=production

CMD ["/app/run.sh"]
