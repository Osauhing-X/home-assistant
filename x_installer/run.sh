#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Config.yaml-st
REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_COMPONENTS_DIR="/homeassistant/custom_components"
mkdir -p "$TMP_DIR"
mkdir -p "$CUSTOM_COMPONENTS_DIR"

copy_plugin() {
    local SRC="$1"
    local NAME="$2"
    local DEST="$CUSTOM_COMPONENTS_DIR/$NAME"

    if [[ ! -d "$DEST" ]]; then
        echo "  Installing new plugin: $NAME → $DEST"
        cp -r "$SRC" "$DEST"
    else
        EXISTING_VERSION=$(jq -r '.version // empty' "$DEST/manifest.json")
        NEW_VERSION=$(jq -r '.version // empty' "$SRC/manifest.json")
        if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
            echo "  Updating plugin $NAME: $EXISTING_VERSION -> $NEW_VERSION"
            rm -rf "$DEST"
            cp -r "$SRC" "$DEST"
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
    if [[ -z "$EXTRACTED_PLUGINS" ]]; then
        echo "No plugins directory found in repo $REPO_URL, skipping..."
        return
    fi

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

# Esmane kontroll kõigi repode jaoks
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "Plugin check complete."
echo "=== Initial plugin update job finished ==="

# Igah tunnine kontroll
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done