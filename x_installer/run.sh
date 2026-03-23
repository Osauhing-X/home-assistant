#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Folder Debug ==="
echo "Current working directory: $(pwd)"
echo

# Funktsioon: kuvab ainult kaustad ja nende alamkaustad (üks tase)
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

# Listi root kaust ja tavaliselt kasutatavad kaustad
list_folders "/"
list_folders "/config"
list_folders "/homeassistant"
list_folders "/plugins"