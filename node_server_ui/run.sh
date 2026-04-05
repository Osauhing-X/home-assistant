#!/usr/bin/with-contenv bashio
set -e

BASE_DIR="/server"
STATUS_FILE="/data/status.json"
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

mkdir -p "$BASE_DIR"
[ ! -f "$STATUS_FILE" ] && echo "{}" > "$STATUS_FILE"

# --- Helper function to update status.json safely ---
update_status() {
    local name=$1
    local key=$2
    local value=$3
    jq --arg n "$name" --arg k "$key" --argjson v "$value" \
       '.[$n][$k]=$v' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
}

# --- Loop through repos ---
IFS=$'\n'
for repo in $REPOS; do
    [ -z "$repo" ] && continue

    NAME=$(basename "$repo" .git)
    DIR="$BASE_DIR/app_$NAME"

    echo "=== $NAME ==="

    # Only clone if directory doesn't exist
    if [ ! -d "$DIR" ]; then
        git clone --depth 1 https://$TOKEN@github.com/$repo "$DIR"
        [ -f "$DIR/package.json" ] && (cd "$DIR" && npm install --omit=dev)
    fi

    # Ensure .env exists
    echo "$ENV_CONTENT" > "$DIR/.env"

    # Init status if missing
    if ! jq -e "has(\"$NAME\")" "$STATUS_FILE" >/dev/null; then
        jq --arg n "$NAME" '.[$n]={status:"stopped",pid:null,error:"",keep_alive:false}' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
    fi
done

# --- Start watchdog for each node ---
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
            KEEP_ALIVE=$(echo "$DATA" | jq -r --arg n "$NAME" '.[$n].keep_alive')

            # --- Only start if status is running, no error, and not already running ---
            if [[ "$STATUS" == "running" && "$ERROR" == "" ]]; then
                if kill -0 "$PID" 2>/dev/null; then
                    sleep 2
                    continue
                fi

                echo "[$(date)] Starting $NAME..."
                cd "$DIR"

                # Detach process, redirect stdout/stderr to log
                nohup node index.js >> "$DIR/log.txt" 2>&1 &
                NEW_PID=$!

                update_status "$NAME" "pid" "$NEW_PID"
                update_status "$NAME" "status" "running"

                # Wait in subshell so main script is not blocked
                wait $NEW_PID
                EXIT_CODE=$?

                if [[ $EXIT_CODE -ne 0 ]]; then
                    echo "[$(date)] $NAME crashed"
                    update_status "$NAME" "status" "stopped"
                    update_status "$NAME" "error" "\"crashed\""
                    update_status "$NAME" "pid" "null"
                else
                    update_status "$NAME" "status" "stopped"
                    update_status "$NAME" "error" "\"\""
                    update_status "$NAME" "pid" "null"
                fi
            fi

            # --- Keep-alive restart logic ---
            if [[ "$KEEP_ALIVE" == "true" && "$STATUS" == "stopped" && "$ERROR" == "" ]]; then
                update_status "$NAME" "status" "running"
            fi

            sleep 2
        done
    ) &
done

# --- Start SvelteKit UI in detached manner ---
(
    echo "Starting SvelteKit UI on port 3000..."
    nohup node build/index.js >> /data/ui.log 2>&1 &
) &