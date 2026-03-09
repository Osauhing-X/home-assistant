#!/usr/bin/with-contenv bashio
set -e

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')
BASE_DIR="/server"

# Kustutame kogu serveri sisu kord käivitamisel
rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"

IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="
  git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # Watchdog loop: restart kui kukub
  [ -f "$DIR/index.js" ] && (
    cd "$DIR"
    while true; do
      echo "[$(date)] Starting $NAME..."
      node index.js
      echo "[$(date)] $NAME exited. Restarting in 3s..."
      sleep 3
    done
  )
done