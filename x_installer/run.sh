#!/usr/bin/with-contenv bashio
set -euo pipefail

echo "=== X Plugins Installer Add-on starting ==="
echo "Plugin check started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Config.yaml-st
REPOS=($(bashio::config 'repo'))
INTERVAL=$(bashio::config 'interval')

TMP_DIR="/tmp/plugins_tmp"
CUSTOM_COMPONENTS_DIR="/homeassistant/custom_components"
PENDING_FILE="/tmp/pending_updates.json"

mkdir -p "$TMP_DIR" "$CUSTOM_COMPONENTS_DIR"
[[ ! -f "$PENDING_FILE" ]] && echo '{}' > "$PENDING_FILE"

# --- Notify HA ---
notify_ha() {
    local TITLE="$1" MSG="$2"
    echo "Notify HA: $TITLE - $MSG"
    curl -s -X POST -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
         -H "Content-Type: application/json" \
         http://supervisor/core/api/services/persistent_notification/create \
         -d "{\"title\":\"$TITLE\",\"message\":\"$MSG\"}" >/dev/null
}

# --- Queue update ---
queue_update() {
    local NAME="$1" OLD="$2" NEW="$3" CHANGELOG="$4" SRC="$5"
    echo "Queue update: $NAME $OLD -> $NEW"
    jq --arg n "$NAME" --arg old "$OLD" --arg new "$NEW" \
       --arg log "$CHANGELOG" --arg src "$SRC" \
       '.[$n] = {"installed":$old,"latest":$new,"changelog":$log,"src":$src}' \
       "$PENDING_FILE" > "$PENDING_FILE.tmp" && mv "$PENDING_FILE.tmp" "$PENDING_FILE"
    notify_ha "Plugin update available" "$NAME: $OLD → $NEW. Approve update to apply."
}

# --- Copy plugin + inject updater.py ---
copy_plugin() {
    local SRC="$1"
    local NAME="$2"
    local DEST="$CUSTOM_COMPONENTS_DIR/$NAME"

    if [[ ! -d "$DEST" ]]; then
        echo "Installing new plugin: $NAME → $DEST"
        cp -r "$SRC" "$DEST"
    else
        local EXISTING=$(jq -r '.version // empty' "$DEST/manifest.json")
        local NEW=$(jq -r '.version // empty' "$SRC/manifest.json")
        local CHANGELOG=$(jq -r '.changelog // ""' "$SRC/manifest.json")
        if [[ "$EXISTING" != "$NEW" ]]; then
            echo "Update available for $NAME: $EXISTING -> $NEW"
            queue_update "$NAME" "$EXISTING" "$NEW" "$CHANGELOG" "$SRC"
        else
            echo "Plugin $NAME up to date (version $EXISTING)"
        fi
        rm -rf "$DEST"
        cp -r "$SRC" "$DEST"
    fi

    # --- inject updater.py ---
    UPDATER_FILE="$DEST/updater.py"
    cat > "$UPDATER_FILE" <<EOL
from homeassistant.components.update import UpdateEntity
import json, os

PLUGIN_ID = "$NAME"
JSON_FILE = "/tmp/pending_updates.json"

class PluginUpdate(UpdateEntity):
    def __init__(self, hass):
        self.hass = hass
        self.plugin_id = PLUGIN_ID
        self._data = {}

    @property
    def installed_version(self):
        return self._data.get("installed")

    @property
    def latest_version(self):
        return self._data.get("latest")

    @property
    def release_summary(self):
        return self._data.get("changelog", "")

    @property
    def can_install(self):
        return self.installed_version != self.latest_version

    async def async_install(self, **kwargs):
        await self.hass.services.async_call(
            "x_installer", "install_update", {"plugin_id": self.plugin_id}
        )

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if not os.path.exists(JSON_FILE):
        return
    with open(JSON_FILE) as f:
        plugins = json.load(f)
    if PLUGIN_ID in plugins:
        update_entity = PluginUpdate(hass)
        update_entity._data = plugins[PLUGIN_ID]
        async_add_entities([update_entity])
EOL
}

# --- Process repo ---
process_repo() {
    local REPO="$1"
    echo "--- Checking repo: $REPO ---"
    local ZIP_URL="${REPO%.git}/archive/refs/heads/main.zip"
    echo "Downloading plugins from $ZIP_URL"
    unzip -q -o <(curl -L -s "$ZIP_URL") -d "$TMP_DIR"
    local PLUGINS_DIR
    PLUGINS_DIR=$(find "$TMP_DIR" -type d -name "plugins" | head -n1)
    [[ -z "$PLUGINS_DIR" ]] && { echo "No plugins directory found, skipping..."; return; }

    for DIR in "$PLUGINS_DIR"/*; do
        [[ -d "$DIR" ]] || continue
        local MANIFEST="$DIR/manifest.json"
        [[ -f "$MANIFEST" ]] || { echo "Skipping $(basename "$DIR") — no manifest.json"; continue; }
        [[ $(jq -r '.x // empty' "$MANIFEST") != "true" ]] && { echo "Skipping $(basename "$DIR") — x not true"; continue; }
        local NAME=$(jq -r '.domain // empty' "$MANIFEST")
        [[ -z "$NAME" ]] && { echo "Skipping $(basename "$DIR") — no domain"; continue; }
        copy_plugin "$DIR" "$NAME"
    done
}

# --- Initial check ---
for REPO in "${REPOS[@]}"; do process_repo "$REPO"; done
echo "Plugin check complete. Initial job finished."

# --- Scheduled check ---
while true; do
    sleep "$INTERVAL"
    echo "=== Scheduled plugin update started at $(date '+%Y-%m-%d %H:%M:%S') ==="
    for REPO in "${REPOS[@]}"; do process_repo "$REPO"; done
    echo "=== Scheduled plugin update finished ==="
done