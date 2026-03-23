#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Starting ==="

PLUGINS_DIR="/plugins"
IGNORE_DIRS="/proc /sys /dev /run /tmp"

# Loeme add-on options.path
OPTIONS_PATH=$(bashio::config 'path' || echo "")

# Funktsioon: otsib rekursiivselt esimese custom_components kausta
find_first_custom_components() {
    local BASE=$1
    find "$BASE" -type d -name "custom_components" \
        $(for d in $IGNORE_DIRS; do echo -prune -o -path $d -prune; done) 2>/dev/null | head -n 1
}

TARGET_HA=""

if [ -n "$OPTIONS_PATH" ]; then
    if [ -d "$OPTIONS_PATH" ]; then
        TARGET_HA="$OPTIONS_PATH"
        echo "Using configured HA path: $TARGET_HA"
    else
        echo "Error: Configured path does not exist: $OPTIONS_PATH"
        exit 1
    fi
else
    echo "No path configured, searching filesystem..."
    TARGET_HA=$(find_first_custom_components "/")
    if [ -z "$TARGET_HA" ]; then
        echo "Error: Cannot find any HA custom_components folder!"
        exit 1
    fi
    echo "Found HA custom_components folder: $TARGET_HA"
fi

# Kopeeri pluginad
for plugin in "$PLUGINS_DIR"/*; do
    PLUGIN_NAME=$(basename "$plugin")
    DEST="$TARGET_HA/$PLUGIN_NAME"

    if [ ! -d "$DEST" ]; then
        echo "Copying $PLUGIN_NAME → $DEST"
        cp -r "$plugin" "$DEST"
    else
        echo "Plugin $PLUGIN_NAME already exists, skipping..."
    fi
done

echo "=== NodeJS Plugin Installer Finished ==="