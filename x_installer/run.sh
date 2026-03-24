#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

REPO=$(bashio::config 'repo')
INTERVAL=$(bashio::config 'interval')

DEST_DIR="/config/custom_components"
TMP_DIR="/tmp/plugins_tmp"

# GitHub owner
GITHUB_OWNER=$(echo "$REPO" | sed -E 's#https://github.com/([^/]+)/.*#\1#')

# FIX: õige zip URL
ZIP_URL="${REPO%.git}/archive/refs/heads/main.zip"

echo "Using repo: $REPO"
echo "Resolved ZIP URL: $ZIP_URL"

while true; do
    echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "--- Checking plugins ---"

    rm -rf "$TMP_DIR"
    mkdir -p "$TMP_DIR"

    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading plugins..."
    curl -L -o "$ZIP_FILE" "$ZIP_URL"

    echo "Extracting..."
    unzip -q "$ZIP_FILE" -d "$TMP_DIR"

    # Leia plugins kaust
    PLUGIN_DIR=$(find "$TMP_DIR" -type d -name "plugins" | head -n 1)

    if [[ -z "$PLUGIN_DIR" ]]; then
        echo "ERROR: plugins folder not found!"
        exit 1
    fi

    for PLUGIN_PATH in "$PLUGIN_DIR"/*; do
        [[ -d "$PLUGIN_PATH" ]] || continue

        MANIFEST="$PLUGIN_PATH/manifest.json"
        [[ -f "$MANIFEST" ]] || continue

        DOMAIN=$(jq -r '.domain' "$MANIFEST")
        REMOTE_VERSION=$(jq -r '.version' "$MANIFEST")
        MAINTAINER=$(jq -r '.maintainer' "$MANIFEST")

        # turvalisus
        if [[ "$MAINTAINER" != "$GITHUB_OWNER" ]]; then
            echo "Skipping $DOMAIN (maintainer mismatch)"
            continue
        fi

        LOCAL_MANIFEST="$DEST_DIR/$DOMAIN/manifest.json"

        UPDATE=false

        if [[ -f "$LOCAL_MANIFEST" ]]; then
            LOCAL_VERSION=$(jq -r '.version' "$LOCAL_MANIFEST")

            if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
                echo "Updating $DOMAIN: $LOCAL_VERSION → $REMOTE_VERSION"
                UPDATE=true
            else
                echo "OK $DOMAIN (version $LOCAL_VERSION)"
            fi
        else
            echo "Installing new plugin $DOMAIN"
            UPDATE=true
        fi

        if $UPDATE; then
            rm -rf "$DEST_DIR/$DOMAIN"
            cp -r "$PLUGIN_PATH" "$DEST_DIR/$DOMAIN"
            echo "$DOMAIN installed."
        fi
    done

    echo "Plugin check complete."

    sleep "$INTERVAL"
done