import json
import logging
from pathlib import Path

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import callback

from .const import DOMAIN, SIGNAL_INTEGRATION_UPDATES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    known = set()

    def add_updates():
        updates = hass.data[DOMAIN][entry.entry_id].setdefault("integration_updates", {})
        # X Entities must be able to advertise its own staged update even before
        # the bridge has delivered its first payload.
        if DOMAIN not in updates:
            updates.setdefault(
                DOMAIN,
                {"id": DOMAIN, "name": "X Entities", "domain": DOMAIN},
            )
        new = []
        for integration_id in updates:
            if integration_id not in known:
                known.add(integration_id)
                new.append(ManagedIntegrationUpdateEntity(hass, entry, integration_id))
        if new:
            async_add_entities(new)
        for entity in hass.data[DOMAIN][entry.entry_id].get("update_entities", []):
            entity.async_write_ha_state()

    add_updates()

    @callback
    def handle_updates(entry_id):
        if entry_id == entry.entry_id:
            add_updates()

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_INTEGRATION_UPDATES, handle_updates))


class ManagedIntegrationUpdateEntity(UpdateEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(self, hass, entry, integration_id):
        self.hass = hass
        self.entry = entry
        self.integration_id = integration_id
        self._attr_unique_id = f"x_managed_integration_{integration_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("service_name", "X Platform").lower().replace(" ", "_"))},
            "name": entry.data.get("service_name", "X Platform"),
            "manufacturer": "Osaühing X",
            "model": "X Integration Manager",
        }

    @property
    def data(self):
        return self.hass.data[DOMAIN][self.entry.entry_id].get("integration_updates", {}).get(self.integration_id, {})

    @property
    def name(self):
        return self.data.get("name") or self.data.get("domain") or self.integration_id

    @property
    def installed_version(self):
        if self.data.get("domain") == DOMAIN:
            return self._manifest_version(self._integration_path / "manifest.json") or self.data.get("installed_version", "unknown")
        return self.data.get("installed_version", "unknown")

    @property
    def latest_version(self):
        if self.data.get("domain") == DOMAIN:
            return self._manifest_version(self._integration_path / "new_version" / "manifest.json") or self.installed_version
        return self.data.get("latest_version", self.installed_version)

    @property
    def _integration_path(self):
        return Path(self.hass.config.path("custom_components", DOMAIN))

    @staticmethod
    def _manifest_version(path):
        try:
            return str(json.loads(path.read_text(encoding="utf-8")).get("version") or "")
        except (OSError, ValueError, TypeError):
            return ""

    @property
    def release_summary(self):
        return f"Managed by X Platform · {self.data.get('domain', '')}"

    @property
    def extra_state_attributes(self):
        return {"x_integration_id": self.integration_id}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        entities = self.hass.data[DOMAIN][self.entry.entry_id].setdefault("update_entities", [])
        entities.append(self)
        self.async_on_remove(lambda: entities.remove(self) if self in entities else None)

    async def async_install(self, version, backup, **kwargs):
        session = self.hass.data[DOMAIN]["_runtime"]["session"]
        url = f"http://{self.entry.data['host']}:{self.entry.data['port']}/api/integrations/update"
        integration_id = self.integration_id
        try:
            async with session.post(url, json={"integrationId": integration_id, "restartHomeAssistant": True}, timeout=15) as response:
                if response.status != 200:
                    raise HomeAssistantError(f"X Platform returned HTTP {response.status}")
        except Exception as error:
            raise HomeAssistantError(f"Failed to queue integration update: {error}") from error
