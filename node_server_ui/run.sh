#!/usr/bin/with-contenv bashio
set -e

# --- Config & paths ---
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')
BASE_DIR="/server"
STATUS_FILE="$BASE_DIR/status.json"

mkdir -p "$BASE_DIR"

# --- Init empty status.json if missing ---
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- Function to update status.json safely ---
update_status() {
  local name=$1
  local pid=$2
  local status=$3
  local boot=$4
  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --argjson b "$boot" \
     '.[$n] = {pid: $p, status: $s, boot_on_start: $b}' \
     "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # Clone or pull repo
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  else
    (cd "$DIR" && git pull --rebase)
  fi

  # Set .env
  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # Initialize status.json for new node
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    update_status "$NAME" "null" "stopped" "true"   # default boot_on_start true
  fi

  # --- Watchdog loop ---
  (
    while true; do
      # Load current status
      DATA=$(cat "$STATUS_FILE")
      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      BOOT_ON_START=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].boot_on_start')

      # Only start if boot_on_start is true and status is stopped
      if [[ "$STATUS" == "stopped" && "$BOOT_ON_START" == "true" ]]; then
        echo "[$(date)] Starting $NAME..."
        cd "$DIR"
        node index.js &
        PID=$!
        update_status "$NAME" "$PID" "running" "$BOOT_ON_START"
        wait $PID
        echo "[$(date)] $NAME exited, setting status to stopped..."
        update_status "$NAME" "null" "stopped" "$BOOT_ON_START"
      fi

      sleep 3
    done
  ) &
done

# --- Start SvelteKit UI on port 3000 ---
while true; do
  echo "Starting SvelteKit UI on port 3000..."
  node build/index.js
  echo "UI crashed, restarting in 2s..."
  sleep 2
done