ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

# Node.js ja bash
RUN apk add --no-cache nodejs npm bash git jq

WORKDIR /app

# Kopeeri run.sh ja tee käivitatavaks
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Kopeeri package.json ja installi sõltuvused
COPY package.json package-lock.json* ./
RUN npm install

# Kopeeri ülejäänud failid
COPY . .

# Build SvelteKit Node server
RUN npm run build

# CMD käivitab addon
CMD [ "/run.sh" ]