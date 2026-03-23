#!/usr/bin/with-contenv bashio
set -e

BASE_DIR="/plugins"
HA_CUSTOM_COMPONENTS="/homeassistant/custom_components"

mkdir -p "$HA_CUSTOM_COMPONENTS"

for plugin in "$BASE_DIR"/*; do
    DEST="$HA_CUSTOM_COMPONENTS/$(basename "$plugin")"
    if [ ! -d "$DEST" ]; then
        echo "Copying $(basename "$plugin") → $DEST"
        cp -r "$plugin" "$DEST"
    else
        echo "Plugin $(basename "$plugin") already exists, skipping..."
    fi
done

echo "All plugins copied. Contents of $HA_CUSTOM_COMPONENTS:"
ls -1 "$HA_CUSTOM_COMPONENTS"