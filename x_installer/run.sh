#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

CUSTOM_DIR="/homeassistant/custom_components"

mkdir -p "$CUSTOM_DIR"

# -------------------------
# Funktsioon ajutise plugin update kopeerimiseks
# -------------------------
copy_plugin_update() {
    local SRC="$1"
    local NAME="$2"
    local DEST="$CUSTOM_DIR/$NAME"
    local TMP_UPDATE="/tmp/${NAME}_new"

    rm -rf "$TMP_UPDATE"
    mkdir -p "$TMP_UPDATE"

    cp -r "$SRC"/. "$TMP_UPDATE" || {
        echo "ERROR: Failed to copy $NAME"
        return
    }

    if [[ ! -f "$TMP_UPDATE/manifest.json" ]]; then
        echo "ERROR: manifest.json missing for $NAME"
        rm -rf "$TMP_UPDATE"
        return
    fi

    NEW_VERSION=$(jq -r '.version // empty' "$TMP_UPDATE/manifest.json")
    EXISTING_VERSION=""

    if [[ -f "$DEST/manifest.json" ]]; then
        EXISTING_VERSION=$(jq -r '.version // empty' "$DEST/manifest.json")
    fi

    if [[ ! -f "$DEST/manifest.json" ]]; then
        echo "Installing $NAME ($NEW_VERSION)"
        rm -rf "$DEST"
        mv "$TMP_UPDATE" "$DEST"
        return
    fi

    if [[ "$EXISTING_VERSION" != "$NEW_VERSION" ]]; then
        echo "Updating $NAME: $EXISTING_VERSION -> $NEW_VERSION"
        rm -rf "$DEST"
        mv "$TMP_UPDATE" "$DEST"
        return
    fi

    echo "Plugin $NAME up to date ($EXISTING_VERSION)"
    rm -rf "$TMP_UPDATE"
}



# -------------------------
# Repo töötlemine
# -------------------------
process_repo() {
    local REPO_URL="$1"
    local REPO_CLEAN=${REPO_URL%.git}
    local ZIP_URL="$REPO_CLEAN/archive/refs/heads/main.zip"
    local ZIP_FILE="/tmp/plugins.zip"

    curl -L -s "$ZIP_URL" -o "$ZIP_FILE"
    unzip -q -o "$ZIP_FILE" -d "/tmp"

    PLUGINS_DIR=$(find /tmp -type d -name "plugins" | head -n1)
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

    rm -rf "$PLUGINS_DIR"
    rm -f "$ZIP_FILE"
}

# -------------------------
# Esmane kontroll
# -------------------------
for REPO in "${REPOS[@]}"; do
    process_repo "$REPO"
done

echo "=== Plugin check complete ==="

# -------------------------
# Igah tunnine loop
# -------------------------
while true; do
    sleep "$INTERVAL"
    for REPO in "${REPOS[@]}"; do
        process_repo "$REPO"
    done
done