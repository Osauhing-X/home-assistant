#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_DIR="/homeassistant/custom_components"
mkdir -p "$TMP_DIR"
mkdir -p "$CUSTOM_DIR"

copy_plugin_update() {
    local SRC="$1"
    local NAME="$2"
    local DEST="$CUSTOM_DIR/$NAME"

    # Tee ajutine kaust temp
    TMP_DEST="$TMP_DIR/${NAME}_update"
    rm -rf "$TMP_DEST"
    cp -r "$SRC" "$TMP_DEST"

    # Loe versioonid
    EXISTING_VERSION=$(jq -r '.version // empty' "$DEST/manifest.json" 2>/dev/null || echo "")
    NEW_VERSION=$(jq -r '.version // empty' "$TMP_DEST/manifest.json")

    if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
        echo "Update available for $NAME: $EXISTING_VERSION -> $NEW_VERSION"
        touch "$DEST/.update_available"
        # temp kaust jääb /tmp, rakendatakse alles Apply Updates ajal
    else
        echo "Plugin $NAME up to date ($EXISTING_VERSION)"
        rm -f "$DEST/.update_available"
        rm -rf "$TMP_DEST"
    fi
}

process_repo() {
    local REPO_URL="$1"
    REPO_CLEAN=${REPO_URL%.git}
    ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    ZIP_FILE="$TMP_DIR/plugins.zip"

    curl -L -s "$ZIP_URL" -o "$ZIP_FILE"
    unzip -q -o "$ZIP_FILE" -d "$TMP_DIR"

    PLUGINS_DIR=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)
    [[ -z "$PLUGINS_DIR" ]] && return

    for PLUGIN_DIR in "$PLUGINS_DIR"/*; do
        [[ -d "$PLUGIN_DIR" ]] || continue
        MANIFEST="$PLUGIN_DIR/manifest.json"
        [[ -f "$MANIFEST" ]] || continue

        X_VALUE=$(jq -r '.x // empty' "$MANIFEST")
        [[ "$X_VALUE" == "true" ]] || continue

        PLUGIN_NAME=$(basename "$PLUGIN_DIR")
        copy_plugin_update "$PLUGIN_DIR" "$PLUGIN_NAME"
    done
}

for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "=== Plugin check complete ==="

# Igah tunnine kontroll
while true; do
    sleep "$INTERVAL"
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
done