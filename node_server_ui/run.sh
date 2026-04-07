#!/usr/bin/with-contenv bashio
set -e

# =========================================================
# BASE CONFIGURATION
# =========================================================
BASE_DIR="/server"
STATUS_FILE="/data/status.json"

ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# =========================================================
# SAFE JSON FIELD UPDATE
# =========================================================
update_field() {
  local name=$1
  local field=$2
  local value=$3

  jq --arg n "$name" --arg f "$field" --argjson v "$value" \
    '.[$n][$f]=$v' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# =========================================================
# LOGGING (UI + FILE + OPTIONAL HA)
# =========================================================
append_log() {
  local name=$1
  local msg="[$(date '+%H:%M:%S')] $2"
  local file="/data/${name}.log"

  touch "$file"

  # Write to file
  echo "$msg" >> "$file"

  # Store in UI (limit to last 200 lines)
  jq --arg n "$name" --arg m "$msg" \
    '.[$n].logs += [$m] | .[$n].logs |= (if length > 200 then .[-200:] else . end)' \
    "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"

  # Also print to HA logs (only system-level logs)
  echo "$msg"
}

# =========================================================
# KILL FULL PROCESS TREE (IMPORTANT FIX)
# =========================================================
kill_tree() {
  local pid=$1

  if kill -0 "$pid" 2>/dev/null; then
    # Kill child processes first
    for child in $(pgrep -P "$pid"); do
      kill_tree "$child"
    done

    kill "$pid" 2>/dev/null || true
    sleep 1

    # Force kill if still alive
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  fi
}

# =========================================================
# INIT / CLONE REPOS
# =========================================================
IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  LOG_FILE="/data/${NAME}.log"
  ERR_FILE="/data/${NAME}.err.log"

  touch "$LOG_FILE" "$ERR_FILE"

  # Initialize JSON entry if missing
  if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
    jq --arg n "$NAME" \
      '.[$n]={status:"stopped",pid:null,error:"",keep_alive:false,crash_count:0,last_crash:0,logs:[]}' \
      "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi

  append_log "$NAME" "Initializing..."

  # Clone if missing
  if [ ! -d "$DIR" ]; then
    append_log "$NAME" "Cloning repository..."
    git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR" >>"$LOG_FILE" 2>&1

    echo "$ENV_CONTENT" > "$DIR/.env"

    if [ -f "$DIR/package.json" ]; then
      append_log "$NAME" "Installing dependencies..."
      (cd "$DIR" && npm install >>"$LOG_FILE" 2>&1)
    fi

    append_log "$NAME" "Clone completed"
  fi
done

# =========================================================
# WATCHDOG LOOP PER APPLICATION
# =========================================================
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

      # =====================================================
      # HARD CRASH DETECTION (process died unexpectedly)
      # =====================================================
      if [[ "$STATUS" == "running" && "$PID" != "null" ]]; then
        if ! kill -0 "$PID" 2>/dev/null; then
          append_log "$NAME" "Process crashed unexpectedly"

          RAW_ERROR=$(cat "$ERR_FILE")
          LAST_ERROR=$(printf "%s" "$RAW_ERROR" | jq -Rs .)

          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "error" "$LAST_ERROR"
          update_field "$NAME" "pid" "null"

          # Send errors to HA logs
          while IFS= read -r line; do
            echo "[$NAME][ERROR] $line"
          done <<< "$RAW_ERROR"

          continue
        fi
      fi

      # =====================================================
      # FORCE STOP (UI requested stop)
      # =====================================================
      if [[ "$STATUS" == "stopped" && "$PID" != "null" ]]; then
        append_log "$NAME" "Stopping process (PID $PID)"

        kill_tree "$PID"

        update_field "$NAME" "pid" "null"
        append_log "$NAME" "Process stopped"
      fi

      # =====================================================
      # START APPLICATION
      # =====================================================
      if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then

        # Already running
        if [[ "$PID" != "null" ]] && kill -0 "$PID" 2>/dev/null; then
          sleep 2
          continue
        fi

        append_log "$NAME" "Starting application..."
        cd "$DIR"

        : > "$LOG_FILE"
        : > "$ERR_FILE"

        node index.js >"$LOG_FILE" 2>"$ERR_FILE" &
        NEW_PID=$!

        append_log "$NAME" "Started with PID $NEW_PID"

        update_field "$NAME" "pid" "$NEW_PID"

        # Pipe ONLY errors to HA logs
        (
          tail -F "$ERR_FILE" | while IFS= read -r line; do
            echo "[$NAME][ERROR] $line"
          done
        ) &

        # Wait for process exit
        wait $NEW_PID
        EXIT_CODE=$?

        append_log "$NAME" "Exited with code $EXIT_CODE"

        # =====================================================
        # CRASH HANDLING + LOOP PROTECTION
        # =====================================================
        if [[ $EXIT_CODE -ne 0 ]]; then
          RAW_ERROR=$(cat "$ERR_FILE")
          LAST_ERROR=$(printf "%s" "$RAW_ERROR" | jq -Rs .)

          update_field "$NAME" "error" "$LAST_ERROR"

          # Crash loop detection (within 30s)
          if (( NOW - LAST_CRASH < 30 )); then
            CRASH_COUNT=$((CRASH_COUNT + 1))
          else
            CRASH_COUNT=1
          fi

          update_field "$NAME" "crash_count" "$CRASH_COUNT"
          update_field "$NAME" "last_crash" "$NOW"

          append_log "$NAME" "Crash count: $CRASH_COUNT"

          if (( CRASH_COUNT >= 3 )); then
            append_log "$NAME" "Crash loop detected → stopping"

            update_field "$NAME" "error" "\"crash_loop\""
            update_field "$NAME" "status" "\"stopped\""
            update_field "$NAME" "pid" "null"
            continue
          fi

          # Backoff restart delay
          sleep $((CRASH_COUNT * 3))

          update_field "$NAME" "status" "\"running\""
          update_field "$NAME" "pid" "null"

        else
          # Normal exit
          update_field "$NAME" "error" "\"\""
          update_field "$NAME" "status" "\"stopped\""
          update_field "$NAME" "pid" "null"
          update_field "$NAME" "crash_count" "0"

          append_log "$NAME" "Stopped normally"
        fi
      fi

      # =====================================================
      # KEEP ALIVE (auto restart)
      # =====================================================
      if [[ "$KEEP" == "true" && "$STATUS" == "stopped" && "$ERROR" == "" ]]; then
        append_log "$NAME" "Restarting (keep_alive)"
        update_field "$NAME" "status" "\"running\""
      fi

      sleep 2
    done
  ) &
done

# =========================================================
# START UI
# =========================================================
append_log "ha-server" "Starting SvelteKit UI on port 3000..."
exec node build/index.js