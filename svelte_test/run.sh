#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080


# loe HA config.yaml otse bashio kaudu
export THEMOVIEDB_API=$(bashio::config 'themoviedb_api')
# export PUBLIC_URL=$(bashio::config 'api_url')
# export PUBLIC_INTERVAL=$(bashio::config 'refresh_interval')


echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js