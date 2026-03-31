#!/usr/bin/with-contenv bashio
set -euo pipefail

CUSTOM_COMPONENTS_DIR="/homeassistant/custom_components"

for DIR in "$CUSTOM_COMPONENTS_DIR"/*; do
    [[ -d "$DIR.update" ]] || continue
    echo "Applying update for $(basename "$DIR")..."
    rm -rf "$DIR"
    mv "$DIR.update" "$DIR"
    rm -f "$DIR/.update_available"
done

echo "All updates applied successfully."