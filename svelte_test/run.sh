#!/usr/bin/with-contenv bashio
set -e


# määrame Node serveri porti
export PORT=8080


# tee .env fail SvelteKit brauserile
cat > .env <<EOF
PUBLIC_URL="${bashio::config 'api_url'}"
PUBLIC_REFRESH="${bashio::config 'refresh_interval'}"
EOF


echo ".env created:"
cat .env


echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js