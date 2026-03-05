#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080


# loe HA config.yaml otse bashio kaudu
export PUBLIC_URL=$(bashio::config 'api_url')
export PUBLIC_INTERVAL=$(bashio::config 'refresh_interval')


# tee .env fail SvelteKit brauserile
cat > .env <<EOF
VITE_URL="${PUBLIC_URL}"
VITE_REFRESH="${PUBLIC_INTERVAL}"
EOF


echo ".env created:"
cat .env

echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js