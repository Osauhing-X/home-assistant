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
  local error=$4
  local keep_alive=$5

  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --arg e "$error" \
     --argjson k "$keep_alive" \
     '.[$n].pid=$p | .[$n].status=$s | .[$n].error=$e | .[$n].keep_alive=$k' \
     "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # Clone repo only if not exists
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
    [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)
  fi

  # Set .env
  echo "$ENV_CONTENT" > "$DIR/.env"

  # Initialize status.json for new node
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    # esimesel installil automaatselt käima, keep_alive default false
    update_status "$NAME" "null" "stopped" "" "false"
  fi

  # --- Watchdog loop ---
  (
    while true; do
      DATA=$(cat "$STATUS_FILE")

      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error')
      KEEP_ALIVE=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].keep_alive')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid')

      # kui juba jookseb, siis jätame
      if [[ "$STATUS" == "running" && "$PID" != "null" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi
      fi

      # --- Käivitamine ---
      # Node käivitatakse ainult, kui:
      # 1. status on running ja error pole (crash) ja keep_alive on true
      if [[ "$STATUS" == "running" || "$KEEP_ALIVE" == "true" ]]; then
        if [[ "$ERROR" == "" ]]; then
          echo "[$(date)] Starting $NAME..."
          cd "$DIR"
          node index.js &
          NEW_PID=$!
          update_status "$NAME" "$NEW_PID" "running" "" "$KEEP_ALIVE"
          wait $NEW_PID

          EXIT_CODE=$?
          if [[ $EXIT_CODE -ne 0 ]]; then
            echo "[$(date)] $NAME crashed with code $EXIT_CODE"
            update_status "$NAME" "null" "stopped" "Crashed (code $EXIT_CODE)" "$KEEP_ALIVE"
          else
            echo "[$(date)] $NAME exited normally"
            update_status "$NAME" "null" "stopped" "" "$KEEP_ALIVE"
          fi
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