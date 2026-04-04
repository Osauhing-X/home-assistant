#!/usr/bin/with-contenv bashio
set -e

# --- CONFIG ---
ENV_CONTENT=$(bashio::config 'env')
REPOS=$(bashio::config 'repo')
TOKEN=$(bashio::config 'github_token')

BASE_DIR="/server"
STATUS_FILE="$BASE_DIR/status.json"

mkdir -p "$BASE_DIR"

# --- INIT STATUS FILE ---
# Kui ei eksisteeri → loo tühi
if [ ! -f "$STATUS_FILE" ]; then
  echo "{}" > "$STATUS_FILE"
fi

# --- SYNC REPOS -> STATUS.JSON ---
# Lisab uued repos ja eemaldab kustutatud
TMP=$(mktemp)
echo "{}" > "$TMP"

IFS=$'\n'
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)

  # kui juba olemas → säilita state
  EXISTS=$(jq -r --arg name "$NAME" 'has($name)' "$STATUS_FILE")

  if [ "$EXISTS" = "true" ]; then
    jq --arg name "$NAME" \
      '.[$name] = input[$name]' \
      "$TMP" "$STATUS_FILE" > "$TMP.2" && mv "$TMP.2" "$TMP"
  else
    # uus repo → default state
    jq --arg name "$NAME" \
      '.[$name] = {enabled: false, boot_on_start: true, status: "stopped"}' \
      "$TMP" > "$TMP.2" && mv "$TMP.2" "$TMP"
  fi
done

mv "$TMP" "$STATUS_FILE"

# --- CLONE / UPDATE REPOS ---
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

  if [ -f "$DIR/package.json" ]; then
    (cd "$DIR" && npm install --omit=dev)
  fi
done

# --- BOOT ON START LOGIC ---
# Käivitab ainult need, millel boot_on_start = true
DATA=$(cat "$STATUS_FILE")

echo "$DATA" | jq -r 'keys[]' | while read name; do
  BOOT=$(echo "$DATA" | jq -r --arg name "$name" '.[$name].boot_on_start')

  if [ "$BOOT" = "true" ]; then
    jq --arg name "$name" '.[$name].enabled = true' \
      "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  fi
done

# --- WATCHDOG LOOP PER APP ---
for repo in $REPOS; do
  [ -z "$repo" ] && continue

  NAME=$(basename "$repo" .git)
  DIR="$BASE_DIR/app_$NAME"

  if [ -f "$DIR/index.js" ]; then
    (
      cd "$DIR"

      # infinite loop → kontrollitud watchdog
      while true; do

        # kas app peab töötama?
        ENABLED=$(jq -r --arg name "$NAME" '.[$name].enabled // false' "$STATUS_FILE")

        if [ "$ENABLED" != "true" ]; then
          sleep 2
          continue
        fi

        echo "[$(date)] Starting $NAME..."

        node index.js &
        PID=$!

        # salvesta PID + status
        jq --arg name "$NAME" --arg pid "$PID" \
          '.[$name].pid = ($pid|tonumber) | .[$name].status = "running"' \
          "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"

        # oota kuni process sureb
        wait $PID

        echo "[$(date)] $NAME exited"

        # märgi stopped
        jq --arg name "$NAME" \
          '.[$name].status = "stopped"' \
          "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"

        sleep 2
      done

    ) &
  fi
done

# --- START SVELTE UI (MAIN PROCESS) ---
export PORT=3000
export HOST=0.0.0.0

while true; do
  echo "Starting SvelteKit UI..."
  node build/index.js
  echo "UI crashed, restarting..."
  sleep 2
done