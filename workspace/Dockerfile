# Shared Core 68cf554; verified linux/amd64 and linux/arm64 image index.
ARG CORE_IMAGE=ghcr.io/osauhing-x/workspace-core@sha256:0729874030a657a048ffea3fd5fe3a5263a6fa5d2fd27d18f4f884bc7867485b
FROM ${CORE_IMAGE}
ENV WORKSPACE_HOST_PLATFORM=home-assistant CORE_DATA_PATH=/data HOST=0.0.0.0 PORT=3000
COPY --chmod=755 run.sh /usr/local/bin/workspace-home-assistant
ENTRYPOINT ["/usr/local/bin/workspace-home-assistant"]
CMD ["node", "runtime/core-server.js"]
