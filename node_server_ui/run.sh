#!/usr/bin/with-contenv bashio
set -e

BASE_DIR="/server"
STATUS_FILE="/data/status.json"

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- SAFE JSON UPDATE ---
update_field() {
  local name=$1
  local field=$2
  local value=$3

  jq --arg n "$name" --arg f "$field" --argjson v "$value" \
    '.[$n][$f]=$v' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- INIT / CLONE ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  echo "=== $NAME ==="

  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
    echo "$ENV_CONTENT" > "$DIR/.env"
    [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)
  fi

  # init status if missing (IMPORTANT: ei override!)
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" \
      '.[$n]={status:"stopped",pid:null,error:"",keep_alive:false}' \
      "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi
done

# --- WATCHDOG ---
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  (
    while true; do
      DATA=$(cat "$STATUS_FILE")

      STATUS=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].status')
      PID=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].pid')
      ERROR=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].error')
      KEEP=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].keep_alive')

      # --- CASE: peab jooksma ---
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then

        # juba jookseb
        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        echo "[$(date)] Starting $NAME..."
        cd "$DIR"

        node index.js >> "$DIR/log.txt" 2>&1 &
        NEW_PID=$!

        update_field "$NAME" "pid" "$NEW_PID"
        update_field "$NAME" "status" "\"running\""

        wait $NEW_PID
        EXIT_CODE=$?

        if [[ $EXIT_CODE -ne 0 ]]; then
          echo "[$(date)] $NAME crashed"
          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "error" "\"crashed\""
          update_field "$NAME" "pid" "null"
        else
          echo "[$(date)] $NAME stopped normally"
          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "pid" "null"
        fi
      fi

      # --- KEEP ALIVE ---
      if [[ "$KEEP" == "true" && "$STATUS" == "stopped" && "$ERROR" == "" ]]; then
        update_field "$NAME" "status" "\"running\""
      fi

      sleep 2
    done
  ) &
done

# ❗ KRITILINE: UI peab olema foregroundis
echo "Starting SvelteKit UI on port 3000..."
exec node build/index.js