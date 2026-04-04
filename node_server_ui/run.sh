#!/usr/bin/with-contenv bashio
set -e

# --- Config & paths ---
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

BASE_DIR="/server"
STATUS_FILE="$BASE_DIR/status.json"

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- Function to update a single node in status.json ---
update_status() {
  local name=$1
  local pid=$2
  local status=$3
  # säilitame kõik muud väljad, uuendame ainult pid ja status
  jq --arg n "$name" --argjson p "$pid" --arg s "$status" \
     '.[$n].pid = $p | .[$n].status = $s' \
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

  # --- Initialize status.json for new node only if missing ---
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" '.[$n] = {pid: null, status: "stopped", boot_on_start: true, manual_stop: false}' \
       "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi

  # --- Watchdog loop ---
  (
    while true; do
      DATA=$(cat "$STATUS_FILE")
      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      BOOT=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].boot_on_start // false')
      MANUAL=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].manual_stop // false')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid // empty')

      # --- Kui node töötab ja PID elus → jätame rahule ---
      if [[ "$STATUS" == "running" ]] && [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        sleep 2
        continue
      fi

      # --- Kui node peaks jooksma, aga PID puudub või crash --- 
      if [[ "$STATUS" == "running" ]] && ([[ -z "$PID" ]] || ! kill -0 "$PID" 2>/dev/null); then
        echo "[$(date)] $NAME crashed või PID puudub, märgime status stopped"
        update_status "$NAME" null "stopped"
        STATUS="stopped"
      fi

      # --- Käivitame ainult juhul, kui boot_on_start=true ja manual_stop=false ---
      if [[ "$STATUS" == "stopped" && "$BOOT" == "true" && "$MANUAL" != "true" ]]; then
        echo "[$(date)] Starting $NAME..."
        cd "$DIR"
        node index.js &
        NEW_PID=$!
        update_status "$NAME" "$NEW_PID" "running"
        wait $NEW_PID
        echo "[$(date)] $NAME exited"
        update_status "$NAME" null "stopped"
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