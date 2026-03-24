#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="

mapfile -t REPOS < <(bashio::config 'repos[]')
INTERVAL=$(bashio::config 'interval')

DEST_DIR="/config/custom_components"
BASE_TMP="/tmp/repos"

mkdir -p "$DEST_DIR"
mkdir -p "$BASE_TMP"

while true; do
    echo ""
    echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

    for REPO in "${REPOS[@]}"; do
        echo "--- Processing repo: $REPO ---"

        REPO_NAME=$(basename "$REPO" .git)
        REPO_DIR="$BASE_TMP/$REPO_NAME"

        # clone või update
        if [[ -d "$REPO_DIR/.git" ]]; then
            echo "Updating repo..."
            git -C "$REPO_DIR" pull --quiet
        else
            echo "Cloning repo..."
            git clone --depth=1 "$REPO" "$REPO_DIR" --quiet
        fi

        PLUGIN_DIR="$REPO_DIR/plugins"

        if [[ ! -d "$PLUGIN_DIR" ]]; then
            echo "No plugins folder → skip"
            continue
        fi

        for PLUGIN_PATH in "$PLUGIN_DIR"/*; do
            [[ -d "$PLUGIN_PATH" ]] || continue

            MANIFEST="$PLUGIN_PATH/manifest.json"
            [[ -f "$MANIFEST" ]] || continue

            DOMAIN=$(jq -r '.domain // empty' "$MANIFEST")
            REMOTE_VERSION=$(jq -r '.version // empty' "$MANIFEST")
            X_FLAG=$(jq -r '.x // false' "$MANIFEST")

            if [[ -z "$DOMAIN" || -z "$REMOTE_VERSION" ]]; then
                echo "Invalid manifest → skip"
                continue
            fi

            if [[ "$X_FLAG" != "true" ]]; then
                echo "Skipping $DOMAIN (x != true)"
                continue
            fi

            LOCAL_DIR="$DEST_DIR/$DOMAIN"
            LOCAL_MANIFEST="$LOCAL_DIR/manifest.json"
            UPDATE=false

            if [[ -f "$LOCAL_MANIFEST" ]]; then
                LOCAL_X=$(jq -r '.x // false' "$LOCAL_MANIFEST")

                if [[ "$LOCAL_X" != "true" ]]; then
                    echo "Skipping $DOMAIN (local not managed)"
                    continue
                fi

                LOCAL_VERSION=$(jq -r '.version // empty' "$LOCAL_MANIFEST")

                if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
                    echo "Updating $DOMAIN: $LOCAL_VERSION → $REMOTE_VERSION"
                    UPDATE=true
                else
                    echo "OK $DOMAIN"
                fi
            else
                echo "Installing $DOMAIN"
                UPDATE=true
            fi

            if $UPDATE; then
                rm -rf "$LOCAL_DIR"
                cp -r "$PLUGIN_PATH" "$LOCAL_DIR"
                echo "$DOMAIN installed."
            fi
        done
    done

    echo "Plugin check complete."
    sleep "$INTERVAL"
done