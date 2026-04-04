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
  local field=$2
  local value=$3

  local tmp=$(mktemp)
  jq --arg n "$name" --arg f "$field" --arg v "$value" \
     '.[$n][$f] = $v' "$STATUS_FILE" > "$tmp" && mv "$tmp" "$STATUS_FILE"
}

# --- Initialize nodes from repos ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  # Clone only if missing
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
  fi

  # Install dependencies
  echo "$ENV_CONTENT" > "$DIR/.env"
  [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)

  # Initialize status.json if missing
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" '.[$n] = {pid:null,status:"stopped",error:"",keep_alive:false}' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi
done

# --- Watchdog for each node ---
for repo in $REPOS; do
  [ -z "$repo" ] && continue
  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  (
    while true; do
      DATA=$(cat "$STATUS_FILE")
      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid')
      KEEP_ALIVE=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].keep_alive')

      # --- Node already running? check pid ---
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        # Node crashed
        echo "[$(date)] $NAME crashed"
        update_status "$NAME" "error" "crashed"
        update_status "$NAME" "status" "stopped"
        continue
      fi

      # --- Start node if keep_alive or manually started ---
      if [[ ("$STATUS" == "running" && "$ERROR" == "") || "$KEEP_ALIVE" == "true" ]]; then
        echo "[$(date)] Starting $NAME..."
        cd "$DIR"
        node index.js &
        NEW_PID=$!
        update_status "$NAME" "pid" "$NEW_PID"
        update_status "$NAME" "status" "running"
        wait $NEW_PID
        # If exits, mark stopped unless keep_alive triggers restart
        if [[ "$ERROR" == "" ]]; then
          update_status "$NAME" "status" "stopped"
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