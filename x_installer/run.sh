#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Debug Mode ==="
echo "Current working directory: $(pwd)"
echo

# Funktsioon, mis loetavalt kuvab kausta sisu
list_folder() {
    local FOLDER=$1
    if [ -d "$FOLDER" ]; then
        echo "Contents of $FOLDER:"
        for entry in "$FOLDER"/*; do
            if [ -e "$entry" ]; then
                if [ -d "$entry" ]; then
                    echo "  [DIR]  $(basename "$entry")"
                    # Näita ka subkaustade sisu (1 tase)
                    for sub in "$entry"/*; do
                        [ -e "$sub" ] && echo "      - $(basename "$sub")"
                    done
                else
                    echo "  [FILE] $(basename "$entry")"
                fi
            fi
        done
        echo
    else
        echo "$FOLDER does not exist"
        echo
    fi
}

# Loenda root kaust
list_folder "/"

# Kontrolli tavaliselt kasutatavaid HA kaustu
list_folder "/config"
list_folder "/homeassistant"
list_folder "/plugins"