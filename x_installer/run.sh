#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Starting ==="

PLUGINS_DIR="/plugins"

# Loeme add-on options.path
OPTIONS_PATH=$(bashio::config 'path' || echo "")

TARGET_HA=""

# Kui path on määratud ja olemas
if [ -n "$OPTIONS_PATH" ] && [ -d "$OPTIONS_PATH" ]; then
    TARGET_HA="$OPTIONS_PATH"
    echo "Using configured HA path: $TARGET_HA"
# Kui path tühi, proovime fallback mountid
elif [ -d "/config/custom_components" ]; then
    TARGET_HA="/config/custom_components"
    echo "Found HA custom_components folder: $TARGET_HA"
elif [ -d "/homeassistant_config/custom_components" ]; then
    TARGET_HA="/homeassistant_config/custom_components"
    echo "Found HA custom_components folder: $TARGET_HA"
else
    echo "Error: Cannot find HA custom_components folder!"
    exit 1
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