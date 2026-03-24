#!/usr/bin/with-contenv bashio
set -e

echo "=== Plugin Installer starting ==="
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')"

REPO="https://github.com/Osauhing-X/home-assistant.git"
CLONE_DIR="/tmp/repo"
PLUGIN_SRC="$CLONE_DIR/plugins"
TARGET="/homeassistant/custom_components"
MAINTAINER="osaühing x"

mkdir -p "$TARGET"

update_plugins() {
    UPDATED=false

    echo ""
    echo "=== Checking for updates: $(date '+%H:%M:%S') ==="

    rm -rf "$CLONE_DIR"
    git clone --depth 1 "$REPO" "$CLONE_DIR"

    for plugin in "$PLUGIN_SRC"/*; do
        [ -d "$plugin" ] || continue

        NAME=$(basename "$plugin")
        DEST="$TARGET/$NAME"

        echo "→ $NAME"

        if [ -d "$DEST" ]; then
            if [ -f "$DEST/manifest.json" ]; then

                if grep -q "\"maintainer\": \"$MAINTAINER\"" "$DEST/manifest.json"; then

                    SRC_VER=$(grep '"version"' "$plugin/manifest.json" | cut -d '"' -f4)
                    DEST_VER=$(grep '"version"' "$DEST/manifest.json" | cut -d '"' -f4 || echo "0")

                    if [ "$SRC_VER" != "$DEST_VER" ]; then
                        echo "✔ Updating $NAME ($DEST_VER → $SRC_VER)"
                        rm -rf "$DEST"
                        cp -r "$plugin" "$DEST"
                        UPDATED=true
                    else
                        echo "✓ Up-to-date"
                    fi

                else
                    echo "⚠ Not our plugin → skip"
                fi
            fi
        else
            echo "➕ Installing $NAME"
            cp -r "$plugin" "$DEST"
            UPDATED=true
        fi
    done

    # 🔥 Restart ainult kui vaja
    if [ "$UPDATED" = true ]; then
        echo "⚡ Changes detected → restarting Home Assistant..."

        curl -s -X POST \
            -H "Authorization: Bearer $(bashio::supervisor.token)" \
            -H "Content-Type: application/json" \
            http://supervisor/core/restart

    else
        echo "No updates → no restart"
    fi
}

# 🔁 Loop
while true; do
    update_plugins
    echo "Sleeping 1h..."
    sleep 3600
done