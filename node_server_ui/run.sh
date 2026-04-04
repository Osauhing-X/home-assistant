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

# --- Function to safely update status.json ---
update_status() {
  local name=$1
  local pid=$2
  local status=$3
  local manual=$4
  local error=$5
  local version=$6
  tmp=$(mktemp)
  jq --arg n "$name" \
     --argjson p "$pid" \
     --arg s "$status" \
     --argjson m "$manual" \
     --arg e "$error" \
     --arg v "$version" \
     'if has($n) then
        .[$n] |= . + {pid: $p, status: $s, manual_stop: $m, error_message: $e, version: $v}
      else
        .[$n] = {pid: $p, status: $s, manual_stop: $m, error_message: $e, version: $v}
      end' "$STATUS_FILE" > "$tmp" && mv "$tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # --- Clone repo ainult esimesel korral ---
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  fi

  # --- Set .env ja install ---
  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # --- Get current version (git commit hash) ---
  VERSION=$(cd "$DIR" && git rev-parse --short HEAD || echo "unknown")

  # --- Init status.json ainult kui app puudub ---
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    # first install → auto start
    update_status "$NAME" "null" "running" "false" "null" "$VERSION"
  else
    # uuenda ainult version
    DATA=$(cat "$STATUS_FILE")
    OLD_VERSION=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].version')
    if [[ "$OLD_VERSION" != "$VERSION" ]]; then
      # uus pull → kustuta error_message
      ERROR=$(jq -r --arg n "$NAME" '.[$n].error_message' "$STATUS_FILE")
      MANUAL=$(jq -r --arg n "$NAME" '.[$n].manual_stop' "$STATUS_FILE")
      STATUS=$(jq -r --arg n "$NAME" '.[$n].status' "$STATUS_FILE")
      update_status "$NAME" "null" "$STATUS" "$MANUAL" "null" "$VERSION"
    fi
  fi

  # --- Watchdog loop ---
  (
  while true; do
    DATA=$(cat "$STATUS_FILE")
    STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
    MANUAL=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].manual_stop')
    ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error_message')
    PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid')

    # --- Kui app peaks jooksema ja ei ole crash ---
    if [[ "$STATUS" == "running" && "$MANUAL" != "true" && "$ERROR" == "null" ]]; then
      if [[ "$PID" != "null" ]] && kill -0 "$PID" 2>/dev/null; then
        sleep 2
        continue
      fi

      echo "[$(date)] Starting $NAME..."
      cd "$DIR"
      # Node output → capture error
      node index.js 2> >(while read line; do
        echo "[${NAME} ERROR] $line"
      done) &
      NEW_PID=$!
      update_status "$NAME" "$NEW_PID" "running" "$MANUAL" "null" "$VERSION"

      # ootame protsessi
      wait $NEW_PID
      echo "[$(date)] $NAME exited"

      # kui crash → salvesta error_message ja pane stopp
      if [[ "$MANUAL" != "true" ]]; then
        update_status "$NAME" "null" "stopped" "$MANUAL" "crashed" "$VERSION"
      else
        # manual stop → jäta seisma
        update_status "$NAME" "null" "stopped" "$MANUAL" "null" "$VERSION"
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