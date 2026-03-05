#!/usr/bin/with-contenv bashio
set -e

# määrame Node serveri porti
export PORT=8080

# Kui keskkonnamuutujad puuduvad, jäta tühjaks
export URL="${ADDON_API_URL:-}"
export INTERVAL="${ADDON_REFRESH_INTERVAL:-}"

# tee .env fail SvelteKit buildi jaoks
cat > .env <<EOF
VITE_ADDON_API_URL="${URL}"
VITE_ADDON_REFRESH_INTERVAL="${INTERVAL}"
EOF

echo ".env created:"
cat .env

echo "Starting SvelteKit Node server on port $PORT..."
node build/index.js