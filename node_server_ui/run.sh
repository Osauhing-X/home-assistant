#!/usr/bin/with-contenv bashio
set -e

# --- BASE SETTINGS ---
BASE_DIR="/server"
STATUS_FILE="/data/status.json"
LOCK_FILE="/tmp/status.lock"

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- SAFE JSON UPDATE WITH FILE LOCK ---
update_field() {
  local name=$1
  local field=$2
  local value=$3

  (
    flock -x 200
    jq --arg n "$name" --arg f "$field" --argjson v "$value" \
      '.[$n][$f]=$v' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  ) 200>"$LOCK_FILE"
}

# --- INIT / CLONE REPOSITORIES ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"
  LOG_FILE="/data/${NAME}.log"
  TAIL_PID_FILE="/data/${NAME}.tail.pid"

  echo "=== $NAME ==="

  # Clone repo if not exists
  if [ ! -d "$DIR" ]; then
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
    echo "$ENV_CONTENT" > "$DIR/.env"
    [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install)
  fi

  # init status if missing
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" \
      '.[$n]={status:"stopped",pid:null,error:"",keep_alive:false,crash_count:0,last_crash:0}' \
      "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi
done

# --- WATCHDOG LOOP PER APP ---
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"
  LOG_FILE="/data/${NAME}.log"
  TAIL_PID_FILE="/data/${NAME}.tail.pid"

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

      # --- HARD CRASH DETECTION ---
      if [[ "$STATUS" == "running" && "$PID" != "null" ]]; then
        if ! kill -0 "$PID" 2>/dev/null; then
          echo "[$(date)] $NAME crashed hard → capturing last logs"

          RAW_ERROR=$(tail -n 50 "$LOG_FILE")
          LAST_ERROR=$(printf "%s" "$RAW_ERROR" | jq -Rs .)

          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "error" "$LAST_ERROR"
          update_field "$NAME" "pid" "null"
          continue
        fi
      fi

      # --- FORCE STOP ---
      if [[ "$STATUS" == "stopped" && "$PID" != "null" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          echo "[$(date)] $NAME force stopping PID $PID"
          kill "$PID" 2>/dev/null || true
          sleep 2
          if kill -0 "$PID" 2>/dev/null; then
            echo "[$(date)] $NAME still alive → SIGKILL PID $PID"
            kill -9 "$PID" 2>/dev/null || true
          fi
        fi
        update_field "$NAME" "pid" "null"
      fi

      # --- START APPLICATION ---
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then

        if [[ "$PID" != "null" ]] && kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        echo "[$(date)] Starting $NAME..."
        cd "$DIR"

        # Clear old log
        : > "$LOG_FILE"

        # Kill old tail
        if [ -f "$TAIL_PID_FILE" ]; then
          OLD_TAIL=$(cat "$TAIL_PID_FILE")
          kill "$OLD_TAIL" 2>/dev/null || true
        fi

        # Start node
        node index.js > "$LOG_FILE" 2>&1 &
        NEW_PID=$!

        # Tail logs to HA
        ( tail -F "$LOG_FILE" | while IFS= read -r line; do
            echo "[$NAME] $line"
          done ) &
        echo $! > "$TAIL_PID_FILE"

        update_field "$NAME" "pid" "$NEW_PID"
        update_field "$NAME" "status" "\"running\""

        # Wait process
        wait $NEW_PID
        EXIT_CODE=$?

        # --- CRASH HANDLING ---
        if [[ $EXIT_CODE -ne 0 ]]; then
          echo "[$(date)] $NAME crashed"

          RAW_ERROR=$(tail -n 50 "$LOG_FILE")
          LAST_ERROR=$(printf "exit:%s\n%s" "$EXIT_CODE" "$RAW_ERROR" | jq -Rs .)
          update_field "$NAME" "error" "$LAST_ERROR"

          if (( NOW - LAST_CRASH < 30 )); then
            CRASH_COUNT=$((CRASH_COUNT + 1))
          else
            CRASH_COUNT=1
          fi
          update_field "$NAME" "crash_count" "$CRASH_COUNT"
          update_field "$NAME" "last_crash" "$NOW"

          if (( CRASH_COUNT >= 3 )); then
            echo "[$(date)] $NAME entered crash loop → stopping"
            update_field "$NAME" "error" "\"crash_loop\""
            update_field "$NAME" "status" "\"stopped\""
            update_field "$NAME" "pid" "null"
            continue
          fi

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

# --- START SVELTEKIT UI ---
echo "Starting SvelteKit UI on port 3000..."
exec node build/index.js