#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080

# loe HA config.yaml otse bashio kaudu
URL=$(bashio::config 'api_url')
INTERVAL=$(bashio::config 'refresh_interval')

# tee .env fail SvelteKit brauserile
cat > .env <<EOF
VITE_ADDON_API_URL="${URL}"
VITE_ADDON_REFRESH_INTERVAL="${INTERVAL}"
EOF

echo ".env created:"
cat .env

echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js