#!/usr/bin/with-contenv bashio
set -e

echo "=== NodeJS Plugin Installer Add-on starting (service mode) ==="

BASE_DIR="/plugins"
HA_CUSTOM_COMPONENTS="/config/custom_components"

# Kopeerime pluginad HA custom_components kausta, ainult kui puuduvad
for plugin in "$BASE_DIR"/*; do
  PLUGIN_NAME=$(basename "$plugin")
  DEST="$HA_CUSTOM_COMPONENTS/$PLUGIN_NAME"
  
  if [ ! -d "$DEST" ]; then
    echo "Copying plugin $PLUGIN_NAME → $HA_CUSTOM_COMPONENTS"
    cp -r "$plugin" "$DEST"
  else
    echo "Plugin $PLUGIN_NAME already exists, skipping..."
  fi
done

# Node.js serveri käivitamine, kui olemas
if [ -f "$BASE_DIR/index.js" ]; then
  (cd "$BASE_DIR"; while true; do
    echo "[$(date)] Starting Node.js server..."
    node index.js
    echo "[$(date)] Node.js server exited, restarting in 3s..."
    sleep 3
  done)
fi

# Hoia konteiner PID 1-s käimas (background service)
tail -f /dev/null