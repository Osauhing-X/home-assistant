#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Folder Debug ==="
echo "Current working directory: $(pwd)"
echo

list_dirs() {
    local FOLDER=$1
    if [ -d "$FOLDER" ]; then
        echo "Directories in $FOLDER:"
        for dir in "$FOLDER"/*; do
            if [ -d "$dir" ]; then
                echo "  $(basename "$dir")"
                # Näita alamkaustu (1 tase)
                for subdir in "$dir"/*; do
                    [ -d "$subdir" ] && echo "      $(basename "$subdir")"
                done
            fi
        done
        echo
    else
        echo "$FOLDER does not exist"
        echo
    fi
}

# Loenda root kaustad ja alamkaustad
list_dirs "/"

# Kontrolli tavaliselt kasutatavaid HA kaustu
list_dirs "/config"
list_dirs "/homeassistant"
list_dirs "/plugins"