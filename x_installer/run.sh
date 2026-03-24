#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Config.yaml-st
REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_COMPONENTS_DIR="/config/custom_components"

mkdir -p "$TMP_DIR"
mkdir -p "$CUSTOM_COMPONENTS_DIR"

# Funktsioon, mis installeerib pluginad kausta
install_plugin() {
    local PLUGIN_DIR="$1"
    local PLUGIN_NAME
    local TARGET_DIR

    PLUGIN_NAME=$(jq -r '.domain' "$PLUGIN_DIR/manifest.json")
    TARGET_DIR="$CUSTOM_COMPONENTS_DIR/$PLUGIN_NAME"
    mkdir -p "$TARGET_DIR"

    # Kui plugin juba olemas, kontrollime versiooni
    if [[ -f "$TARGET_DIR/manifest.json" ]]; then
        EXISTING_VERSION=$(jq -r '.version // empty' "$TARGET_DIR/manifest.json")
        NEW_VERSION=$(jq -r '.version // empty' "$PLUGIN_DIR/manifest.json")
        if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
            echo "  Updating plugin $PLUGIN_NAME: $EXISTING_VERSION -> $NEW_VERSION"
            rm -rf "$TARGET_DIR"
            mkdir -p "$TARGET_DIR"
        else
            echo "  Plugin $PLUGIN_NAME up to date (version $EXISTING_VERSION)"
            return
        fi
    else
        echo "  Installing new plugin: $PLUGIN_NAME"
    fi

    cp -r "$PLUGIN_DIR/"* "$TARGET_DIR/"
    echo "  Installed $PLUGIN_NAME → $TARGET_DIR"
}

# Funktsioon, mis töötleb iga repo
process_repo() {
    local REPO_URL="$1"

    echo "--- Checking repo: $REPO_URL ---"

    # puhasta URL: eemalda .git kui olemas
    REPO_CLEAN=${REPO_URL%.git}
    ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading plugins from $ZIP_URL"
    curl -L -s "$ZIP_URL" -o "$ZIP_FILE"

    # Puhasta vana kaust
    rm -rf "$TMP_DIR/extracted"
    mkdir -p "$TMP_DIR/extracted"

    echo "Extracting plugins..."
    unzip -q "$ZIP_FILE" -d "$TMP_DIR/extracted"

    # Otsime kausta plugins
    EXTRACTED_PLUGINS=$(find "$TMP_DIR/extracted" -type d -name "plugins" | head -n1)
    if [[ -z "$EXTRACTED_PLUGINS" ]]; then
        echo "No plugins directory found in repo $REPO_URL, skipping..."
        return
    fi

    for PLUGIN_DIR in "$EXTRACTED_PLUGINS"/*; do
        if [[ -d "$PLUGIN_DIR" && -f "$PLUGIN_DIR/manifest.json" ]]; then
            X_VALUE=$(jq -r '.x // empty' "$PLUGIN_DIR/manifest.json")
            if [[ "$X_VALUE" == "true" ]]; then
                install_plugin "$PLUGIN_DIR"
            else
                echo "  Skipping $(basename "$PLUGIN_DIR") — x not true"
            fi
        fi
    done
}

# Esimene käivitamine
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "Plugin check complete."

# Tsükliline uuendamine iga INTERVAL sekundi tagant
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done