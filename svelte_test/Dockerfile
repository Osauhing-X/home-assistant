ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

# Node ja bash install
RUN apk add --no-cache nodejs npm bash

# Kopeeri run.sh konteinerisse root-i
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Kopeeri SvelteKit build ja package.json
COPY package.json package-lock.json* ./
RUN npm install
COPY . .

# Build SvelteKit Node server
RUN npm run build

# Käivita skript
CMD [ "/run.sh" ]