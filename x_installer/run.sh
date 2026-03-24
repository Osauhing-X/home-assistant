#!/usr/bin/env bash
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

# CONFIG: loeb config.yaml väärtused
REPO_URL=$(bashio::config 'repo')
INTERVAL=$(bashio::config 'interval')
PLUGINS_DIR="/config/custom_components"

# Tuleta GitHub owner ja repo nimi
GITHUB_OWNER=$(echo "$REPO_URL" | cut -d'/' -f4)
GITHUB_REPO=$(echo "$REPO_URL" | cut -d'/' -f5 | sed 's/\.git//')

echo "Repo URL: $REPO_URL"
echo "Maintainer: $GITHUB_OWNER"
echo "Repo name: $GITHUB_REPO"
echo "Check interval: ${INTERVAL}s"

download_plugins() {
    echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

    TMP_DIR=$(mktemp -d)
    ZIP_FILE="$TMP_DIR/plugins.zip"

    echo "Downloading plugins from $REPO_URL"
    curl -L -s -o "$ZIP_FILE" "$REPO_URL/archive/refs/heads/main.zip"

    echo "Extracting plugins..."
    unzip -q "$ZIP_FILE" -d "$TMP_DIR"

    EXTRACTED_DIR="$TMP_DIR/$GITHUB_REPO-main/plugins"

    if [ ! -d "$EXTRACTED_DIR" ]; then
        echo "Error: /plugins kausta ei leitud ZIP-ist!"
        rm -rf "$TMP_DIR"
        return 1
    fi

    for PLUGIN_PATH in "$EXTRACTED_DIR"/*; do
        [ -d "$PLUGIN_PATH" ] || continue

        MANIFEST="$PLUGIN_PATH/manifest.json"
        if [ ! -f "$MANIFEST" ]; then
            echo "Skipping $(basename "$PLUGIN_PATH"): manifest.json puudub"
            continue
        fi

        DOMAIN=$(jq -r '.domain // empty' "$MANIFEST")
        VERSION=$(jq -r '.version // empty' "$MANIFEST")
        PLUGIN_MAINTAINER=$(jq -r '.maintainer // empty' "$MANIFEST")

        if [ "$PLUGIN_MAINTAINER" != "$GITHUB_OWNER" ]; then
            echo "Skipping $DOMAIN: maintainer mismatch ($PLUGIN_MAINTAINER != $GITHUB_OWNER)"
            continue
        fi

        DEST="$PLUGINS_DIR/$DOMAIN"

        if [ -d "$DEST" ]; then
            echo "Updating plugin $DOMAIN..."
            rm -rf "$DEST"
        else
            echo "Installing new plugin $DOMAIN..."
        fi

        cp -r "$PLUGIN_PATH" "$DEST"
        echo "Installed on $(date '+%Y-%m-%d %H:%M:%S')" > "$DEST/.installed_at"
        echo "Plugin $DOMAIN installed/updated successfully."
    done

    rm -rf "$TMP_DIR"
    echo "Plugin check complete."
}

# Esimene käivitamine
download_plugins

# Tsükliline uuenduste kontroll
while true; do
    echo "Sleeping for $INTERVAL seconds before next check..."
    sleep "$INTERVAL"
    download_plugins
done