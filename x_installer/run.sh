#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== Extaas Plugin Updater starting ==="

REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_COMPONENTS_DIR="/homeassistant/custom_components"
mkdir -p "$TMP_DIR" "$CUSTOM_COMPONENTS_DIR"

copy_plugin_update() {
    local SRC="$1"
    local NAME="$2"
    local DEST="$CUSTOM_COMPONENTS_DIR/$NAME"
    local TMP_UPDATE="$DEST.update"

    EXISTING_VERSION=$(jq -r '.version // empty' "$DEST/manifest.json" 2>/dev/null || echo "")
    NEW_VERSION=$(jq -r '.version // empty' "$SRC/manifest.json")

    if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
        echo "Update available for $NAME: $EXISTING_VERSION -> $NEW_VERSION"
        rm -rf "$TMP_UPDATE"
        cp -r "$SRC" "$TMP_UPDATE"
        touch "$DEST/.update_available"
    else
        echo "$NAME up to date"
        rm -rf "$DEST/.update_available" 2>/dev/null || true
    fi
}

process_repo() {
    local REPO_URL="$1"
    echo "--- Checking repo: $REPO_URL ---"

    REPO_CLEAN=${REPO_URL%.git}
    ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading $ZIP_URL..."
    curl -L -s "$ZIP_URL" -o "$ZIP_FILE"

    unzip -q -o "$ZIP_FILE" -d "$TMP_DIR"

    EXTRACTED_PLUGINS=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)
    [[ -z "$EXTRACTED_PLUGINS" ]] && return

    for PLUGIN_DIR in "$EXTRACTED_PLUGINS"/*; do
        [[ -d "$PLUGIN_DIR" ]] || continue
        MANIFEST="$PLUGIN_DIR/manifest.json"
        [[ -f "$MANIFEST" ]] || continue
        [[ $(jq -r '.x // empty' "$MANIFEST") == "true" ]] || continue

        PLUGIN_NAME=$(basename "$PLUGIN_DIR")
        copy_plugin_update "$PLUGIN_DIR" "$PLUGIN_NAME"
    done
}

# Esmane check
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "=== Initial plugin check finished ==="

# Igah tunnine kordus
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update ==="
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done