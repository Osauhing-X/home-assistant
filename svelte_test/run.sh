#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080


# loe Home Assistant addon config
export THEMOVIEDB_API=$(bashio::config 'themoviedb_api')

# määrame SvelteKit base path HA ingressist
export SVELTEKIT_BASE="/$(bashio::ingress_path)"

# --- Test values
# export PUBLIC_URL=$(bashio::config 'api_url')
# export PUBLIC_INTERVAL=$(bashio::config 'refresh_interval')


echo "Starting SvelteKit Node server on port $PORT with base $SVELTEKIT_BASE..."
node build/index.js