#!/usr/bin/with-contenv bashio
set -e


# määrame Node serveri porti
export PORT=8080


export PUBLIC_URL="$(bashio::config 'api_url')"
export PUBLIC_REFRESH="$(bashio::config 'refresh_interval')"


echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js