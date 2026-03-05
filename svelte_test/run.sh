#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080

# Home Assistant addon options keskkonnamuutujad brauserisse Svelte kaudu
export VITE_ADDON_API_URL="${ADDON_API_URL-}"
export VITE_ADDON_REFRESH_INTERVAL="${ADDON_REFRESH_INTERVAL-}"

echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js