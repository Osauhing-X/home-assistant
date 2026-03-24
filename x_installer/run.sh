#!/usr/bin/with-contenv bashio
set -e

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Loeb repo listi config.yaml-st
REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

# Loob ajutise kausta
TMP_DIR="/tmp/plugins_tmp"
mkdir -p "$TMP_DIR"

for REPO_URL in "${REPOS[@]}"; do
    echo "--- Checking repo: $REPO_URL ---"

    ZIP_FILE="$TMP_DIR/plugins.zip"

    # Lae alla ja ekstrakti
    curl -L "$REPO_URL/archive/refs/heads/main.zip" -o "$ZIP_FILE"
    
    unzip -q "$ZIP_FILE" -d "$TMP_DIR"

    # Oletame, et zip ekstraktib kataloogi home-assistant-main/plugins
    EXTRACTED_DIR=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)

    if [[ -z "$EXTRACTED_DIR" ]]; then
        echo "No plugins folder found in $REPO_URL, skipping..."
        continue
    fi

    for PLUGIN_DIR in "$EXTRACTED_DIR"/*; do
        MANIFEST="$PLUGIN_DIR/manifest.json"
        if [[ ! -f "$MANIFEST" ]]; then
            echo "No manifest.json in $PLUGIN_DIR, skipping..."
            continue
        fi

        # Loe x väärtus
        X_FLAG=$(jq -r '.x' "$MANIFEST")
        DOMAIN=$(jq -r '.domain' "$MANIFEST")
        VERSION=$(jq -r '.version' "$MANIFEST")

        if [[ "$X_FLAG" != "true" ]]; then
            echo "Skipping $DOMAIN (x != true)"
            continue
        fi

        TARGET_DIR="/config/custom_components/$DOMAIN"
        mkdir -p "$TARGET_DIR"

        # Kontrolli versiooni
        if [[ -f "$TARGET_DIR/manifest.json" ]]; then
            CUR_VERSION=$(jq -r '.version' "$TARGET_DIR/manifest.json")
            if [[ "$CUR_VERSION" == "$VERSION" ]]; then
                echo "$DOMAIN is up-to-date ($VERSION)"
                continue
            fi
            echo "Updating $DOMAIN from $CUR_VERSION to $VERSION"
        else
            echo "Installing new plugin $DOMAIN ($VERSION)"
        fi

        # Kopeeri plugin
        cp -r "$PLUGIN_DIR"/* "$TARGET_DIR"/
    done

done

echo "Plugin check complete."