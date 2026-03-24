#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

# --- CONFIG ---
REPO=$(bashio::config 'repo')
INTERVAL=$(bashio::config 'interval')

DEST_DIR="/config/custom_components"
TMP_DIR="/tmp/plugins_tmp"

echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

while true; do
    echo "--- Checking plugins ---"

    # Lae GitHubist zip
    ZIP_URL="${REPO/archive/refs/heads/main}.zip"
    echo "Downloading plugins from $ZIP_URL"

    mkdir -p "$TMP_DIR"
    TMP_ZIP="$TMP_DIR/plugins.zip"

    curl -L -o "$TMP_ZIP" "$ZIP_URL"

    # Paki lahti
    unzip -q "$TMP_ZIP" -d "$TMP_DIR"

    # Pluginide kaust GitHub zip-ist
    # Tavaliselt: home-assistant-main/plugins
    EXTRACTED_DIR=$(find "$TMP_DIR" -type d -name "plugins" | head -n 1)

    if [[ ! -d "$EXTRACTED_DIR" ]]; then
        echo "No plugins directory found in archive!"
        rm -rf "$TMP_DIR"
        sleep "$INTERVAL"
        continue
    fi

    # Itereeri iga plugin kausta läbi
    for PLUGIN_PATH in "$EXTRACTED_DIR"/*; do
        [[ -d "$PLUGIN_PATH" ]] || continue

        MANIFEST="$PLUGIN_PATH/manifest.json"
        if [[ ! -f "$MANIFEST" ]]; then
            echo "Skipping $(basename "$PLUGIN_PATH") - no manifest.json"
            continue
        fi

        # Loeme GITHUB_OWNER ja versiooni
        DOMAIN=$(jq -r '.domain' "$MANIFEST")
        REMOTE_VERSION=$(jq -r '.version' "$MANIFEST")
        GITHUB_OWNER=$(echo "$REPO" | sed -E 's#https://github.com/([^/]+)/.*#\1#')

        # Kontrollime, kas maintainer vastab
        MAINTAINER=$(jq -r '.maintainer' "$MANIFEST")
        if [[ "$MAINTAINER" != "$GITHUB_OWNER" ]]; then
            echo "Skipping $DOMAIN - maintainer mismatch ($MAINTAINER != $GITHUB_OWNER)"
            continue
        fi

        LOCAL_MANIFEST="$DEST_DIR/$DOMAIN/manifest.json"
        UPDATE_PLUGIN=false

        if [[ -f "$LOCAL_MANIFEST" ]]; then
            LOCAL_VERSION=$(jq -r '.version' "$LOCAL_MANIFEST")
            if [[ "$REMOTE_VERSION" != "$LOCAL_VERSION" ]]; then
                echo "Updating $DOMAIN: $LOCAL_VERSION -> $REMOTE_VERSION"
                UPDATE_PLUGIN=true
            else
                echo "Skipping $DOMAIN: version $LOCAL_VERSION is up-to-date"
            fi
        else
            echo "Installing new plugin $DOMAIN..."
            UPDATE_PLUGIN=true
        fi

        if $UPDATE_PLUGIN; then
            rm -rf "$DEST_DIR/$DOMAIN"
            cp -r "$PLUGIN_PATH" "$DEST_DIR/$DOMAIN"
            echo "$DOMAIN installed/updated to version $REMOTE_VERSION"
        fi
    done

    # Cleanup
    rm -rf "$TMP_DIR"

    echo "Plugin check complete at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Oota järgmist tsüklit
    sleep "$INTERVAL"
done