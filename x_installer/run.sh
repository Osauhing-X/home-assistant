#!/usr/bin/with-contenv bashio
set -euo pipefail

# --- Config from addon options ---
REPOS=$(bashio::config 'repo')
INTERVAL=$(bashio::config 'interval')

CUSTOM_COMPONENTS_DIR="/config/custom_components"
TMP_DIR="/tmp/plugins_tmp"

mkdir -p "$CUSTOM_COMPONENTS_DIR"

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# --- Function to install/update a single plugin ---
install_plugin() {
    local PLUGIN_SRC="$1"
    local PLUGIN_NAME
    PLUGIN_NAME=$(basename "$PLUGIN_SRC")
    local DEST="$CUSTOM_COMPONENTS_DIR/$PLUGIN_NAME"
    local MANIFEST="$PLUGIN_SRC/manifest.json"

    # Kontrolli, et manifest.json olemas ja x:true
    if [ ! -f "$MANIFEST" ]; then
        echo "Skipping $PLUGIN_NAME → no manifest.json"
        return
    fi
    local X_FLAG
    X_FLAG=$(jq -r '.x // false' "$MANIFEST")
    if [ "$X_FLAG" != "true" ]; then
        echo "Skipping $PLUGIN_NAME → x:false"
        return
    fi

    # Kui ei eksisteeri, siis kopeeri
    if [ ! -d "$DEST" ]; then
        echo "Installing new plugin: $PLUGIN_NAME"
        cp -r "$PLUGIN_SRC" "$DEST"
    else
        # Kui eksisteerib, kontrolli versiooni
        local SRC_VERSION DEST_VERSION
        SRC_VERSION=$(jq -r '.version // ""' "$MANIFEST")
        DEST_VERSION=$(jq -r '.version // ""' "$DEST/manifest.json")
        if [ "$SRC_VERSION" != "$DEST_VERSION" ]; then
            echo "Updating plugin $PLUGIN_NAME (version $DEST_VERSION → $SRC_VERSION)"
            rm -rf "$DEST"
            cp -r "$PLUGIN_SRC" "$DEST"
        else
            echo "Plugin $PLUGIN_NAME already up-to-date (version $SRC_VERSION)"
        fi
    fi
}

# --- Function to process one repo ---
process_repo() {
    local REPO_URL="$1"
    echo "--- Checking repo: $REPO_URL ---"

    # Download ja unzip
    local ZIP_FILE="$TMP_DIR/plugins.zip"
    rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
    curl -sSL "$REPO_URL/archive/refs/heads/main.zip" -o "$ZIP_FILE"

    local EXTRACTED_DIR PLUGINS_SRC
    unzip -q "$ZIP_FILE" -d "$TMP_DIR"
    EXTRACTED_DIR=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n1) # home-assistant-main
    PLUGINS_SRC="$EXTRACTED_DIR/plugins"

    if [ ! -d "$PLUGINS_SRC" ]; then
        echo "No plugins directory found in $REPO_URL, skipping..."
        return
    fi

    # Käi läbi kõik pluginad
    for plugin in "$PLUGINS_SRC"/*; do
        [ -d "$plugin" ] || continue
        install_plugin "$plugin"
    done
}

# --- Initial check ---
for REPO in $REPOS; do
    process_repo "$REPO"
done

echo "Plugin check complete."

# --- Loop for periodic updates ---
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in $REPOS; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done