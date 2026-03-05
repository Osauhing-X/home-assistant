ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:13.8
FROM $BUILD_FROM

# Node install
RUN apk add --no-cache nodejs npm bash

WORKDIR /app

# Kopeeri failid
COPY package*.json ./
RUN npm install

COPY . .

# Build SvelteKit
RUN npm run build

# Käivita run.sh
CMD [ "/run.sh" ]