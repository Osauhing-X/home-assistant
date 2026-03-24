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
        echo ""
        echo "=============================="
        echo "Checking repo: $REPO"
        echo "=============================="

        REPO_NAME=$(basename "$REPO" .git)
        REPO_DIR="$BASE_TMP/$REPO_NAME"

        if [[ -d "$REPO_DIR/.git" ]]; then
            echo "Updating repo..."
            git -C "$REPO_DIR" pull --quiet || {
                echo "Git pull failed → skip repo"
                continue
            }
        else
            echo "Cloning repo..."
            git clone --depth=1 "$REPO" "$REPO_DIR" --quiet || {
                echo "Git clone failed → skip repo"
                continue
            }
        fi

        echo "Repo path: $REPO_DIR"
        echo "Listing repo root:"
        ls -la "$REPO_DIR"

        PLUGIN_DIR="$REPO_DIR/plugins"

        echo "Looking for plugins in: $PLUGIN_DIR"

        if [[ ! -d "$PLUGIN_DIR" ]]; then
            echo "❌ plugins folder not found → skip"
            continue
        fi

        echo "✅ plugins folder found"
        echo "Listing plugins:"
        ls -la "$PLUGIN_DIR"

        for PLUGIN_PATH in "$PLUGIN_DIR"/*; do
            [[ -d "$PLUGIN_PATH" ]] || continue

            echo ""
            echo "→ Found plugin folder: $PLUGIN_PATH"

            MANIFEST="$PLUGIN_PATH/manifest.json"

            if [[ ! -f "$MANIFEST" ]]; then
                echo "  No manifest.json → skip"
                continue
            fi

            DOMAIN=$(jq -r '.domain // empty' "$MANIFEST")
            REMOTE_VERSION=$(jq -r '.version // empty' "$MANIFEST")
            X_FLAG=$(jq -r '.x // false' "$MANIFEST")

            echo "  Domain: $DOMAIN"
            echo "  Version: $REMOTE_VERSION"
            echo "  x flag: $X_FLAG"

            if [[ -z "$DOMAIN" || -z "$REMOTE_VERSION" ]]; then
                echo "  Invalid manifest → skip"
                continue
            fi

            if [[ "$X_FLAG" != "true" ]]; then
                echo "  Skipping (x != true)"
                continue
            fi

            LOCAL_DIR="$DEST_DIR/$DOMAIN"
            LOCAL_MANIFEST="$LOCAL_DIR/manifest.json"
            UPDATE=false

            if [[ -f "$LOCAL_MANIFEST" ]]; then
                LOCAL_X=$(jq -r '.x // false' "$LOCAL_MANIFEST")

                if [[ "$LOCAL_X" != "true" ]]; then
                    echo "  Skipping (local not managed)"
                    continue
                fi

                LOCAL_VERSION=$(jq -r '.version // empty' "$LOCAL_MANIFEST")

                if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
                    echo "  Updating: $LOCAL_VERSION → $REMOTE_VERSION"
                    UPDATE=true
                else
                    echo "  OK (same version)"
                fi
            else
                echo "  Installing new plugin"
                UPDATE=true
            fi

            if $UPDATE; then
                rm -rf "$LOCAL_DIR"
                cp -r "$PLUGIN_PATH" "$LOCAL_DIR"
                echo "  ✔ Installed"
            fi
        done
    done

    echo ""
    echo "Plugin check complete."
    sleep "$INTERVAL"
done