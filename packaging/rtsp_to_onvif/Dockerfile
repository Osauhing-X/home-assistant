FROM node:24-alpine AS build
ARG APP_REVISION=9665393dc75e539104fafb09f237ccdd731651b2
RUN apk add --no-cache git
WORKDIR /source
RUN git init \
    && git remote add origin https://github.com/Osauhing-X/home-assistant.git \
    && git fetch --depth 1 origin "${APP_REVISION}" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "${APP_REVISION}"
WORKDIR /source/applications/rtsp_to_onvif
RUN npm ci && npm run build && npm prune --omit=dev --ignore-scripts

FROM node:24-alpine
RUN apk add --no-cache ffmpeg iproute2
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
      amd64) MTX_ARCH=amd64; MTX_SHA=a7ba21268fccda3ebc43fdad76b87fddb85ce77e725b5cb637bca724b5394fbe ;; \
      arm64) MTX_ARCH=arm64; MTX_SHA=9e5b38a5b5fcab1916341b024031b2fc5dc6a2059baed9ba3f3b0d3768d231a8 ;; \
      *) echo 'Unsupported target architecture'; exit 1 ;; \
    esac \
    && wget -q "https://github.com/bluenviron/mediamtx/releases/download/v1.19.3/mediamtx_v1.19.3_linux_${MTX_ARCH}.tar.gz" -O /tmp/mediamtx.tar.gz \
    && echo "${MTX_SHA}  /tmp/mediamtx.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/mediamtx.tar.gz -C /usr/local/bin mediamtx \
    && rm /tmp/mediamtx.tar.gz
WORKDIR /app
COPY --from=build /source/applications/rtsp_to_onvif/build ./build
COPY --from=build /source/applications/rtsp_to_onvif/package.json ./package.json
COPY --from=build /source/applications/rtsp_to_onvif/node_modules ./node_modules
COPY run.mjs runtime-options.mjs migration-state.mjs ./
ENV NODE_ENV=production
CMD ["node", "run.mjs"]
