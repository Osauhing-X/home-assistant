#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080

echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js