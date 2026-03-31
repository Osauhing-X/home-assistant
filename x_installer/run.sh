#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Config.yaml-st
REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_COMPONENTS_DIR="/homeassistant/custom_components"
PENDING_FILE="/tmp/pending_updates.json"

mkdir -p "$TMP_DIR" "$CUSTOM_COMPONENTS_DIR"
[[ ! -f "$PENDING_FILE" ]] && echo '{}' > "$PENDING_FILE"

notify_ha() {
    local TITLE="$1"
    local MSG="$2"
    curl -s -X POST \
         -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
         -H "Content-Type: application/json" \
         http://supervisor/core/api/services/persistent_notification/create \
         -d "{\"title\":\"$TITLE\",\"message\":\"$MSG\"}" >/dev/null
}

queue_update() {
    local NAME="$1" OLD="$2" NEW="$3" CHANGELOG="$4" SRC="$5"
    # lisa JSON faili
    jq --arg n "$NAME" --arg old "$OLD" --arg new "$NEW" --arg log "$CHANGELOG" --arg src "$SRC" \
       '.[$n] = {"installed":$old,"latest":$new,"changelog":$log,"src":$src}' \
       "$PENDING_FILE" > "$PENDING_FILE.tmp" && mv "$PENDING_FILE.tmp" "$PENDING_FILE"
    notify_ha "Plugin update available" "$NAME: $OLD → $NEW"
}

copy_plugin() {
    local SRC="$1" NAME="$2" DEST="$CUSTOM_COMPONENTS_DIR/$NAME"

    if [[ ! -d "$DEST" ]]; then
        echo "  Installing new plugin: $NAME → $DEST"
        cp -r "$SRC" "$DEST"
    else
        EXISTING_VERSION=$(jq -r '.version // empty' "$DEST/manifest.json")
        NEW_VERSION=$(jq -r '.version // empty' "$SRC/manifest.json")
        CHANGELOG=$(jq -r '.changelog // ""' "$SRC/manifest.json")

        if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
            echo "  Update available for $NAME: $EXISTING_VERSION -> $NEW_VERSION"
            queue_update "$NAME" "$EXISTING_VERSION" "$NEW_VERSION" "$CHANGELOG" "$SRC"
        else
            echo "  Plugin $NAME up to date (version $EXISTING_VERSION)"
        fi
    fi
}

process_repo() {
    local REPO_URL="$1"
    echo "--- Checking repo: $REPO_URL ---"

    REPO_CLEAN=${REPO_URL%.git}
    ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading plugins from $ZIP_URL"
    curl -L -s "$ZIP_URL" -o "$ZIP_FILE"

    echo "Extracting plugins..."
    unzip -q -o "$ZIP_FILE" -d "$TMP_DIR"

    EXTRACTED_PLUGINS=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)
    [[ -z "$EXTRACTED_PLUGINS" ]] && { echo "No plugins directory found, skipping..."; return; }

    for PLUGIN_DIR in "$EXTRACTED_PLUGINS"/*; do
        [[ -d "$PLUGIN_DIR" ]] || continue
        MANIFEST="$PLUGIN_DIR/manifest.json"
        [[ -f "$MANIFEST" ]] || { echo "  Skipping $(basename "$PLUGIN_DIR") — no manifest.json"; continue; }

        X_VALUE=$(jq -r '.x // empty' "$MANIFEST")
        [[ "$X_VALUE" == "true" ]] || { echo "  Skipping $(basename "$PLUGIN_DIR") — x not true"; continue; }

        PLUGIN_NAME=$(jq -r '.domain' "$MANIFEST")
        copy_plugin "$PLUGIN_DIR" "$PLUGIN_NAME"
    done
}

# User-triggered install
apply_update() {
    local NAME="$1"
    local SRC_DIR=$(jq -r --arg n "$NAME" '.[$n].src // empty' "$PENDING_FILE")
    [[ -z "$SRC_DIR" ]] && return
    echo "Installing plugin $NAME..."
    rm -rf "$CUSTOM_COMPONENTS_DIR/$NAME"
    cp -r "$SRC_DIR" "$CUSTOM_COMPONENTS_DIR/$NAME"
    notify_ha "Plugin updated" "$NAME has been updated. Restart Home Assistant to apply changes."
    # eemalda pending entry
    jq "del(.\"$NAME\")" "$PENDING_FILE" > "$PENDING_FILE.tmp" && mv "$PENDING_FILE.tmp" "$PENDING_FILE"
}

# --- Esmane kontroll kõigi repode jaoks ---
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done
echo "Plugin check complete."
echo "=== Initial plugin update job finished ==="

# --- Igah tunnine kontroll ---
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done