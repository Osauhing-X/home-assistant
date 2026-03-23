#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Starting ==="

PLUGINS_DIR="/plugins"

# Loeme add-on options.path
OPTIONS_PATH=$(bashio::config 'path' || echo "")

TARGET_HA=""

# Kui path on määratud
if [ -n "$OPTIONS_PATH" ]; then
    if [ -d "$OPTIONS_PATH" ]; then
        TARGET_HA="$OPTIONS_PATH"
        echo "Using configured HA path: $TARGET_HA"
    else
        echo "Error: Configured path does not exist: $OPTIONS_PATH"
        exit 1
    fi
else
    # Supervisor add-on puhul mount on /config
    if [ -d "/config/custom_components" ]; then
        TARGET_HA="/config/custom_components"
        echo "Found HA custom_components folder: $TARGET_HA"
    else
        echo "Error: Cannot find /config/custom_components folder!"
        exit 1
    fi
fi

# Kopeeri kõik pluginad
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