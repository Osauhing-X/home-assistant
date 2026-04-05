#!/usr/bin/with-contenv bashio
set -e

# --- Config & paths ---
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

BASE_DIR="/server"
STATUS_FILE="/data/status.json"

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- Function to safely update status.json ---
update_status() {
  local name=$1
  local pid=$2
  local status=$3
  local error=$4
  local keep=$5

  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --arg e "$error" \
     --argjson k "$keep" \
     '.[$n] = {pid: $p, status: $s, error: $e, keep_alive: $k}' \
     "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # Clone only if not olemas
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
    echo "$ENV_CONTENT" > "$DIR/.env"
    [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)
  fi

  # Initialize status if missing
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    update_status "$NAME" "null" "stopped" "" true
  fi

  # --- Watchdog loop ---
  (
  while true; do
    DATA=$(cat "$STATUS_FILE")
    STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
    PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid')
    ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error')
    KEEP=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].keep_alive')

    # Start only if stopped and no error OR keep_alive true
    if [[ "$STATUS" == "stopped" && "$ERROR" == "" && "$KEEP" == "true" ]]; then
      echo "[$(date)] Starting $NAME..."
      cd "$DIR"
      node index.js &
      NEW_PID=$!

      update_status "$NAME" "$NEW_PID" "running" "" "$KEEP"

      wait $NEW_PID
      EXIT_CODE=$?

      if [[ $EXIT_CODE -ne 0 ]]; then
        echo "[$(date)] $NAME crashed"
        update_status "$NAME" "null" "stopped" "crashed" "$KEEP"
      else
        echo "[$(date)] $NAME stopped normally"
        update_status "$NAME" "null" "stopped" "" "$KEEP"
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