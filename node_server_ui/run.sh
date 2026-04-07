#!/usr/bin/with-contenv bashio
set -e

# --- BASE SETTINGS ---
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

# --- APPEND LOG (UI + FILE) ---
append_log() {
  local name=$1
  local msg=$2
  jq --arg n "$name" --arg m "$msg" \
    '.[$n].logs += [$m]' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  echo "$msg" >> "/data/${name}.log"
  echo "$msg" # HA logid
}

# --- INIT / CLONE REPOSITORIES ---
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"
  LOG_FILE="/data/${NAME}.log"
  ERR_FILE="/data/${NAME}.err.log"

  append_log "$NAME" "=== Initializing $NAME ==="

  # Clone repo if missing
  if [ ! -d "$DIR" ]; then
    append_log "$NAME" "Cloning $NAME..."
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR" >>"$LOG_FILE" 2>&1
    echo "$ENV_CONTENT" > "$DIR/.env"
    [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install >>"$LOG_FILE" 2>&1)
    append_log "$NAME" "Clone + npm install done"
  fi

  # Initialize status if missing
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" \
      '.[$n]={status:"stopped",pid:null,error:"",keep_alive:false,crash_count:0,last_crash:0,logs:[]}' \
      "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi
done

# --- WATCHDOG LOOP PER APP ---
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"
  LOG_FILE="/data/${NAME}.log"
  ERR_FILE="/data/${NAME}.err.log"

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
          append_log "$NAME" "$NAME crashed hard → extracting error"

          RAW_ERROR=$(cat "$ERR_FILE")
          LAST_ERROR=$(printf "%s" "$RAW_ERROR" | jq -Rs .)

          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "error" "$LAST_ERROR"
          update_field "$NAME" "pid" "null"

          # HA log immediate
          while IFS= read -r line; do
            echo "[$NAME][ERROR] $line"
          done <<< "$RAW_ERROR"

          continue
        fi
      fi

      # --- FORCE STOP ---
      if [[ "$STATUS" == "stopped" && "$PID" != "null" ]]; then
        if kill -0 "$PID" 2>/dev/null; then
          append_log "$NAME" "$NAME force stopping PID $PID"
          kill "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null
        fi
        update_field "$NAME" "pid" "null"
      fi

      # --- START APPLICATION ---
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then
        if [[ "$PID" != "null" ]] && kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        append_log "$NAME" "Starting $NAME..."
        cd "$DIR"

        : > "$LOG_FILE"
        : > "$ERR_FILE"

        node index.js >"$LOG_FILE" 2>"$ERR_FILE" &
        NEW_PID=$!

        # Pipe node errors to HA log immediately
        ( tail -F "$ERR_FILE" | while IFS= read -r line; do
            echo "[$NAME][ERROR] $line"
          done ) &

        update_field "$NAME" "pid" "$NEW_PID"
        update_field "$NAME" "status" "\"running\""

        wait $NEW_PID
        EXIT_CODE=$?

        if [[ $EXIT_CODE -ne 0 ]]; then
          append_log "$NAME" "$NAME crashed with exit code $EXIT_CODE"

          RAW_ERROR=$(cat "$ERR_FILE")
          LAST_ERROR=$(printf "%s" "$RAW_ERROR" | jq -Rs .)
          update_field "$NAME" "error" "$LAST_ERROR"

          if (( NOW - LAST_CRASH < 30 )); then
            CRASH_COUNT=$((CRASH_COUNT + 1))
          else
            CRASH_COUNT=1
          fi
          update_field "$NAME" "crash_count" "$CRASH_COUNT"
          update_field "$NAME" "last_crash" "$NOW"

          if (( CRASH_COUNT >= 3 )); then
            append_log "$NAME" "$NAME entered crash loop → stopping"
            update_field "$NAME" "error" "\"crash_loop\""
            update_field "$NAME" "status" "\"stopped\""
            update_field "$NAME" "pid" "null"
            continue
          fi

          sleep $((CRASH_COUNT * 3))
          update_field "$NAME" "status" "\"running\""
          update_field "$NAME" "pid" "null"
        else
          append_log "$NAME" "$NAME exited normally"
          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "pid" "null"
          update_field "$NAME" "crash_count" "0"
        fi
      fi

      # --- KEEP ALIVE ---
      if [[ "$KEEP" == "true" && "$STATUS" == "stopped" && "$ERROR" == "" ]]; then
        append_log "$NAME" "$NAME restarting (keep_alive)"
        update_field "$NAME" "status" "\"running\""
      fi

      sleep 2
    done
  ) &
done

# --- START SVELTEKIT UI ---
append_log "ha-server" "Starting SvelteKit UI on port 3000..."
exec node build/index.js