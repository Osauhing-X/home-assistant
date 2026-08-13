# update.py
import logging
import json
import shutil
import asyncio
from pathlib import Path

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


# -------------------------
# Setup entry
# -------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([XEntitiesUpdateEntity(hass, entry)])


# -------------------------
# Update entity
# -------------------------
from .const import DOMAIN
class XEntitiesUpdateEntity(UpdateEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._attr_name = "X Entities"
        self._attr_unique_id = f"x_entities_update_{entry.entry_id}"

        self._attr_installed_version = None
        self._attr_latest_version = None
        self._attr_supported_features = UpdateEntityFeature.INSTALL
        self._attr_extra_state_attributes = {"changelog": []}
  
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("service_name").lower().replace(" ", "_"))},
            "name": entry.data.get("service_name"),
            "manufacturer": "Osaühing X",
            "model": "Service Device" }

    # -------------------------
    # Init
    # -------------------------
    async def async_added_to_hass(self):
        await self.async_update()
        self.async_write_ha_state()

    # -------------------------
    # Install update
    # -------------------------
    async def async_install(self, version, backup, **kwargs):
        base_dir = Path(__file__).resolve().parent
        new_dir = base_dir / "new_version"

        if not new_dir.exists():
            raise HomeAssistantError("No update available")

        def do_update():
            backup_dir = base_dir.parent / f"{base_dir.name}_backup"

            # cleanup vana backup
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # ignore new_version backupis
            def ignore(dir, files):
                return {"new_version"} if "new_version" in files else set()

            shutil.copytree(base_dir, backup_dir, ignore=ignore)

            tmp_dir = base_dir.parent / f"{base_dir.name}_tmp"
            old_dir = base_dir.parent / f"{base_dir.name}_old"

            # cleanup temp
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
            if old_dir.exists():
                shutil.rmtree(old_dir)

            # new_version → tmp
            shutil.move(new_dir, tmp_dir)

            # live → old (safe rename)
            shutil.move(base_dir, old_dir)

            # tmp → live
            shutil.move(tmp_dir, base_dir)

            # cleanup vana versioon
            shutil.rmtree(old_dir)

        await self.hass.async_add_executor_job(do_update)

        # väike delay, et FS settle'iks
        await asyncio.sleep(1)

        # optional: show changelog as persistent notification
        changelog = self._attr_extra_state_attributes.get("changelog", [])
        if changelog:
            await self.hass.services.async_call(
                "persistent_notification",
                "create", {
                    "title": f"Updating {self._attr_name} to {version}",
                    "message": "\n".join(changelog) } )

        # restart HA
        await self.hass.services.async_call(
            "homeassistant",
            "restart",
            blocking=False
        )

    # -------------------------
    # Check update
    # -------------------------
    async def async_update(self):
        try:
            base_dir = Path(__file__).resolve().parent
            new_version_dir = base_dir / "new_version"

            installed_manifest = base_dir / "manifest.json"
            latest_manifest = new_version_dir / "manifest.json"

            installed_data = {}
            latest_data = {}

            # installed version
            if installed_manifest.exists():
                installed_text = await self.hass.async_add_executor_job(
                    installed_manifest.read_text, "utf-8"
                )
                installed_data = json.loads(installed_text)

            # latest version (optional)
            if latest_manifest.exists():
                latest_text = await self.hass.async_add_executor_job(
                    latest_manifest.read_text, "utf-8" )
                latest_data = json.loads(latest_text)

            installed_version = installed_data.get("version", "unknown")
            latest_version = latest_data.get("version", installed_version)
            changelog = latest_data.get("changelog", [])

            self._attr_installed_version = installed_version
            self._attr_latest_version = latest_version
            self._attr_extra_state_attributes = {"changelog": changelog}

            _LOGGER.info(
                "UPDATE ENTITY: installed=%s latest=%s",
                installed_version,
                latest_version,
            )

        except Exception as e:
            _LOGGER.error("Update check failed: %s", e)
            self._attr_installed_version = "unknown"
            self._attr_latest_version = "unknown"
            self._attr_extra_state_attributes = {"changelog": []}

        # 🔥 oluline — UI refresh
        self.async_write_ha_state()