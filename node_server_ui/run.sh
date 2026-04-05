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

# --- INIT ---
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

  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" \
      '.[$n]={status:"running",pid:null,error:"",keep_alive:false,crash_count:0,last_crash:0}' \
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
      CRASH_COUNT=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].crash_count')
      LAST_CRASH=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].last_crash')

      NOW=$(date +%s)

      # --- RUNNING ---
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then

        if kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        echo "[$(date)] Starting $NAME..."
        cd "$DIR"

        (
          node index.js 2>&1 | while IFS= read -r line; do
            echo "[$NAME] $line"
          done
        ) &
        NEW_PID=$!

        update_field "$NAME" "pid" "$NEW_PID"
        update_field "$NAME" "status" "\"running\""

        wait $NEW_PID
        EXIT_CODE=$?

        # --- CRASH HANDLING ---
        if [[ $EXIT_CODE -ne 0 ]]; then
          echo "[$(date)] $NAME crashed"

          # kas crash oli hiljuti?
          if (( NOW - LAST_CRASH < 30 )); then
            CRASH_COUNT=$((CRASH_COUNT + 1))
          else
            CRASH_COUNT=1
          fi

          update_field "$NAME" "crash_count" "$CRASH_COUNT"
          update_field "$NAME" "last_crash" "$NOW"

          # 🔥 CRASH LOOP DETECT
          if (( CRASH_COUNT >= 3 )); then
            echo "[$(date)] $NAME entered crash loop → stopping"
            update_field "$NAME" "error" "\"crash_loop\""
            update_field "$NAME" "status" "\"stopped\""
            update_field "$NAME" "pid" "null"
            continue
          fi

          # backoff
          sleep $((CRASH_COUNT * 3))

          update_field "$NAME" "status" "\"running\""
          update_field "$NAME" "pid" "null"

        else
          echo "[$(date)] $NAME exited normally"
          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "pid" "null"
          update_field "$NAME" "crash_count" "0"
        fi
      fi

      # --- KEEP ALIVE ---
      if [[ "$KEEP" == "true" && "$STATUS" == "stopped" && "$ERROR" == "" ]]; then
        echo "[$(date)] $NAME restarting (keep_alive)"
        update_field "$NAME" "status" "\"running\""
      fi

      sleep 2
    done
  ) &
done

# --- UI ---
echo "Starting SvelteKit UI on port 3000..."
exec node build/index.js