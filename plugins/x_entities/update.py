import logging
import json
from pathlib import Path
from homeassistant.components.update import UpdateEntity

_LOGGER = logging.getLogger(__name__)


# -------------------------
# Setup entry
# -------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    """Register X Entities update entity."""
    async_add_entities([XEntitiesUpdateEntity(hass, entry)])


# -------------------------
# Update entity
# -------------------------
class XEntitiesUpdateEntity(UpdateEntity):
    """Entity, mis näitab X Entities plugin update olemasolu."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._attr_name = "X Entities"
        self._attr_unique_id = f"x_entities_update_{entry.entry_id}"

        # versioonid
        self._attr_installed_version = None
        self._attr_latest_version = None

    async def async_update(self):
        """Kontrolli installitud ja uue versiooni."""
        try:
            base_dir = Path("/homeassistant/custom_components/x_entities")
            new_version_dir = base_dir / "new_version"

            installed_manifest = base_dir / "manifest.json"
            latest_manifest = new_version_dir / "manifest.json"

            # loeme JSON-id turvaliselt
            installed_data = json.loads(installed_manifest.read_text()) if installed_manifest.exists() else {}
            latest_data = json.loads(latest_manifest.read_text()) if latest_manifest.exists() else {}

            installed_version = installed_data.get("version", "unknown")
            latest_version = latest_data.get("version", installed_version)

            self._attr_installed_version = installed_version
            self._attr_latest_version = latest_version

            _LOGGER.debug(
                "X Entities versions: installed=%s, latest=%s",
                installed_version,
                latest_version
            )

        except Exception as e:
            _LOGGER.error("X Entities update version check failed: %s", e)
            self._attr_installed_version = "unknown"
            self._attr_latest_version = "unknown"