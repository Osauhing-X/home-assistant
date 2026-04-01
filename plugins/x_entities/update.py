import logging
import json
from pathlib import Path
from homeassistant.components.update import UpdateEntity

_LOGGER = logging.getLogger(__name__)

# -------------------------
# Setup entry
# -------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([XEntitiesUpdateEntity(hass, entry)])


# -------------------------
# Update entity
# -------------------------
class XEntitiesUpdateEntity(UpdateEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._attr_name = "X Entities"
        self._attr_unique_id = f"x_entities_update_{entry.entry_id}"

        self._attr_installed_version = None
        self._attr_latest_version = None
        self._attr_available = True

    async def async_added_to_hass(self):
        # 🔥 see on puudu sul
        await self.async_update()

    async def async_update(self):
        try:
            base_dir = Path(__file__).resolve().parent
            new_version_dir = base_dir / "new_version"

            installed_manifest = base_dir / "manifest.json"
            latest_manifest = new_version_dir / "manifest.json"

            installed_data = {}
            latest_data = {}

            if installed_manifest.exists():
                installed_data = json.loads(
                    installed_manifest.read_text(encoding="utf-8")
                )

            if latest_manifest.exists():
                latest_data = json.loads(
                    latest_manifest.read_text(encoding="utf-8")
                )

            installed_version = installed_data.get("version", "unknown")
            latest_version = latest_data.get("version", installed_version)

            self._attr_installed_version = installed_version
            self._attr_latest_version = latest_version

            self._attr_available = True

            _LOGGER.warning(
                "UPDATE ENTITY: installed=%s latest=%s",
                installed_version,
                latest_version,
            )

        except Exception as e:
            _LOGGER.error("Update check failed: %s", e)
            self._attr_installed_version = "unknown"
            self._attr_latest_version = "unknown"