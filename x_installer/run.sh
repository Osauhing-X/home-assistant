#!/usr/bin/with-contenv bash
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

# --- Funktsioon: tööta läbi üks repo ---
process_repo() {
    local REPO_URL="$1"
    echo "--- Checking repo: $REPO_URL ---"

    # puhasta URL: eemalda .git kui olemas
    REPO_CLEAN=${REPO_URL%.git}
    ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading plugins from $ZIP_URL"
    curl -L "$ZIP_URL" -o "$ZIP_FILE"

    echo "Extracting plugins..."
    unzip -q "$ZIP_FILE" -d "$TMP_DIR"

    # Otsime kausta plugins
    EXTRACTED_PLUGINS=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)
    if [[ -z "$EXTRACTED_PLUGINS" ]]; then
        echo "No plugins directory found in repo $REPO_URL, skipping..."
        return
    fi

    for PLUGIN_DIR in "$EXTRACTED_PLUGINS"/*; do
        if [[ -d "$PLUGIN_DIR" ]]; then
            MANIFEST="$PLUGIN_DIR/manifest.json"
            if [[ ! -f "$MANIFEST" ]]; then
                echo "  Skipping $(basename "$PLUGIN_DIR") — no manifest.json"
                continue
            fi

            # Kontrollime x:true
            X_VALUE=$(jq -r '.x // empty' "$MANIFEST")
            if [[ "$X_VALUE" != "true" ]]; then
                echo "  Skipping $(basename "$PLUGIN_DIR") — x not true"
                continue
            fi

            PLUGIN_NAME=$(jq -r '.domain' "$MANIFEST")
            TARGET_DIR="$CUSTOM_COMPONENTS_DIR/$PLUGIN_NAME"

            # Kui ei ole olemas, kopeeri
            if [[ ! -d "$TARGET_DIR" ]]; then
                echo "  Installing new plugin: $PLUGIN_NAME"
                cp -r "$PLUGIN_DIR" "$TARGET_DIR"
            else
                # Kontrollime versiooni
                EXISTING_VERSION=$(jq -r '.version // empty' "$TARGET_DIR/manifest.json")
                NEW_VERSION=$(jq -r '.version // empty' "$MANIFEST")
                if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
                    echo "  Updating plugin $PLUGIN_NAME: $EXISTING_VERSION -> $NEW_VERSION"
                    rm -rf "$TARGET_DIR"
                    cp -r "$PLUGIN_DIR" "$TARGET_DIR"
                else
                    echo "  Plugin $PLUGIN_NAME up to date (version $EXISTING_VERSION)"
                fi
            fi
        fi
    done
}

# --- Esimene käivitamine kohe ---
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "Plugin check complete."

# --- Tsükliline ajastatud kontroll ---
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
    echo "=== Scheduled plugin update finished ==="
done