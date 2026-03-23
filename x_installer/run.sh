#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Add-on Starting ==="

# Base plugins folder sees konteineris
PLUGINS_DIR="/plugins"

# Potentsiaalsed HA kaustad
HA_PATHS=(
    "/config/custom_components"
    "/homeassistant/custom_components"
)

# Funktsioon: kuvab ainult kaustad ja alamkaustad (üks tase)
list_folders() {
    local FOLDER=$1
    if [ -d "$FOLDER" ]; then
        echo "Folders in $FOLDER:"
        for dir in "$FOLDER"/*/; do
            [ -d "$dir" ] || continue
            DIR_NAME=$(basename "$dir")
            echo "  [DIR] $DIR_NAME"

            # Näita alamkaustu (üks tase)
            for subdir in "$dir"/*/; do
                [ -d "$subdir" ] || continue
                SUB_NAME=$(basename "$subdir")
                echo "      - $SUB_NAME"
            done
        done
        echo
    else
        echo "$FOLDER does not exist"
        echo
    fi
}

# Leia esimene olemasolev HA kaust
TARGET_HA=""
for path in "${HA_PATHS[@]}"; do
    if [ -d "$path" ]; then
        TARGET_HA="$path"
        break
    fi
done

if [ -z "$TARGET_HA" ]; then
    echo "Error: Cannot find a HA custom_components folder! Make sure /config or /homeassistant is mounted."
    echo "Available folders in root:"
    list_folders "/"
    exit 1
fi

echo "Using HA custom_components folder: $TARGET_HA"
echo

# Kuvame kaustad ja alamkaustad seal
list_folders "$TARGET_HA"

# Kopeerime pluginad
for plugin in "$PLUGINS_DIR"/*; do
    PLUGIN_NAME=$(basename "$plugin")
    DEST="$TARGET_HA/$PLUGIN_NAME"

    if [ ! -d "$DEST" ]; then
        echo "Copying plugin $PLUGIN_NAME → $DEST"
        cp -r "$plugin" "$DEST"
    else
        echo "Plugin $PLUGIN_NAME already exists, skipping..."
    fi
done

echo
echo "=== HA custom_components after copy ==="
list_folders "$TARGET_HA"

# Hoia konteiner töös logimiseks
tail -f /dev/null