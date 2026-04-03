#!/usr/bin/with-contenv bashio
set -e

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')
BASE_DIR="/server"
STATUS_FILE="$BASE_DIR/status.json"

mkdir -p "$BASE_DIR"

# Init empty status
echo "{}" > "$STATUS_FILE"

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  else
    (cd "$DIR" && git pull --rebase)
  fi

  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # Watchdog loop
  if [ -f "$DIR/index.js" ]; then
    (
      cd "$DIR"
      while true; do
        echo "[$(date)] Starting $NAME..."
        node index.js &
        PID=$!
        echo $PID
        # Update status file
        jq --arg name "$NAME" --arg pid "$PID" '.[$name] = { pid: ($pid|tonumber), status: "running" }' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"

        wait $PID
        echo "[$(date)] $NAME exited. Restarting in 3s..."
        # Update status to stopped
        jq --arg name "$NAME" '.[$name].status = "stopped"' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"

        sleep 3
      done
    ) &
  fi
done

# --- Start SvelteKit UI ---
while true; do
  node build/index.js
  echo "UI crashed, restarting..."
  sleep 2
done