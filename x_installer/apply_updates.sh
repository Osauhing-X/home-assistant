#!/usr/bin/with-contenv bashio
set -euo pipefail

CUSTOM_DIR="/homeassistant/custom_components"
TMP_DIR="/tmp/plugins_tmp"

for DIR in "$CUSTOM_DIR"/*; do
    [[ -d "$DIR" ]] || continue
    [[ -f "$DIR/.update_available" ]] || continue

    NAME=$(basename "$DIR")
    TMP_UPDATE="$TMP_DIR/${NAME}_update"

    if [[ -d "$TMP_UPDATE" ]]; then
        echo "Applying update for $NAME"
        rm -rf "$DIR"
        mv "$TMP_UPDATE" "$DIR"
        rm -f "$DIR/.update_available"
    fi
done

echo "All available updates applied."