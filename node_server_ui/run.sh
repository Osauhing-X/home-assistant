#!/usr/bin/with-contenv bashio
set -e

# --- Config & paths ---
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

BASE_DIR="/server"
DATA_DIR="/data"
STATUS_FILE="$DATA_DIR/status.json"

mkdir -p "$BASE_DIR"
mkdir -p "$DATA_DIR"

# --- Init empty status.json if missing ---
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- Function to update status.json safely ---
update_status() {
  local name=$1
  local pid=$2
  local status=$3
  local manual=$4
  local error=$5

  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --argjson m "$manual" \
     --arg e "$error" \
     '.[$n] |= (. // {}) | .[$n].pid = $p | .[$n].status = $s | .[$n].manual_stop = $m | .[$n].error = $e' \
     "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # Clone repo only if missing (uute nodede jaoks)
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  fi

  # Set .env
  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # --- Initialize status.json for new node ---
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    # Esialgne käivitus, node tööle
    cd "$DIR"
    node index.js &
    PID=$!
    update_status "$NAME" "$PID" "running" "false" ""
  fi

  # --- Watchdog loop ---
  (
    while true; do
      DATA=$(cat "$STATUS_FILE")
      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      MANUAL=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].manual_stop')
      ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error // ""')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid // "null"')

      # Kui node peaks jooksma ja pole käsitsi peatatud ega erroris
      if [[ "$STATUS" == "running" && "$MANUAL" != "true" && -z "$ERROR" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        echo "[$(date)] Starting $NAME..."
        cd "$DIR"
        node index.js &
        NEW_PID=$!
        update_status "$NAME" "$NEW_PID" "running" "$MANUAL" ""

        wait $NEW_PID
        EXIT_CODE=$?

        if [[ $EXIT_CODE -ne 0 ]]; then
          echo "[$(date)] $NAME crashed with exit code $EXIT_CODE"
          update_status "$NAME" "null" "stopped" "$MANUAL" "Crashed (exit $EXIT_CODE)"
        else
          echo "[$(date)] $NAME exited normally"
          update_status "$NAME" "null" "stopped" "$MANUAL" ""
        fi
      fi

      sleep 2
    done
  ) &
done

# --- Start SvelteKit UI ---
while true; do
  echo "Starting SvelteKit UI on port 3000..."
  node build/index.js
  echo "UI crashed, restarting in 2s..."
  sleep 2
done