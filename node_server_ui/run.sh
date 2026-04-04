#!/usr/bin/with-contenv bashio
set -e

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

BASE_DIR="/server"
STATUS_FILE="$BASE_DIR/status.json"

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

update_status() {
  local name=$1
  local pid=$2
  local status=$3
  local boot=$4
  local manual=$5
  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --argjson b "$boot" \
     --argjson m "$manual" \
     '.[$n] = {pid: $p, status: $s, boot_on_start: $b, manual_stop: $m}' \
     "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

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

  # --- Initialize status.json if missing ---
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    update_status "$NAME" "null" "stopped" "true" "false"
  fi

  # --- Sync actual running process with status.json ---
  EXIST_PID=$(jq -r --arg n "$NAME" '.[$n].pid // empty' "$STATUS_FILE")
  if [ -n "$EXIST_PID" ] && kill -0 "$EXIST_PID" 2>/dev/null; then
    # Node juba töötab, värskenda status.json
    BOOT=$(jq -r --arg n "$NAME" '.[$n].boot_on_start' "$STATUS_FILE")
    MANUAL=$(jq -r --arg n "$NAME" '.[$n].manual_stop' "$STATUS_FILE")
    update_status "$NAME" "$EXIST_PID" "running" "$BOOT" "$MANUAL"
  fi

  # --- Watchdog loop ---
  (
    while true; do
      DATA=$(cat "$STATUS_FILE")
      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      BOOT=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].boot_on_start')
      MANUAL=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].manual_stop')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid // empty')

      # --- Kui node juba töötab, kontrolli PID-i ---
      if [[ "$STATUS" == "running" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        else
          echo "[$(date)] $NAME crashed, uuendame statusiks stopped"
          update_status "$NAME" "null" "stopped" "$BOOT" "$MANUAL"
        fi
      fi

      # --- Käivita ainult, kui boot_on_start=true ja manual_stop=false ---
      if [[ "$STATUS" == "stopped" && "$BOOT" == "true" && "$MANUAL" != "true" ]]; then
        echo "[$(date)] Starting $NAME..."
        cd "$DIR"
        node index.js &
        NEW_PID=$!
        # Säilita manual_stop väärtus
        update_status "$NAME" "$NEW_PID" "running" "$BOOT" "$MANUAL"

        wait $NEW_PID

        echo "[$(date)] $NAME exited"
        update_status "$NAME" "null" "stopped" "$BOOT" "$MANUAL"
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