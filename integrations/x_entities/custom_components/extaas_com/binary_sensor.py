from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_ENTITY
from .entities import ExtaasBinarySensor


async def async_setup_entry(hass, entry, async_add_entities):
    if entry.data.get("protocol") == "workspace-core":
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        async_add_entities([WorkspaceConnectivity(coordinator, entry)])
        return
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    async_add_entities([
        ExtaasBinarySensor(hass, entry, key)
        for key, value in data.items()
        if value.get("type") == "binary_sensor"
    ])

    @callback
    def handle_new(entry_id, keys):
        if entry_id != entry.entry_id:
            return
        current = hass.data[DOMAIN][entry.entry_id]["entities"]
        entities = [
            ExtaasBinarySensor(hass, entry, key)
            for key in keys
            if current.get(key, {}).get("type") == "binary_sensor"
        ]
        if entities:
            async_add_entities(entities)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ENTITY, handle_new)
    )

class WorkspaceConnectivity(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Connectivity"
    _attr_device_class = "connectivity"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_workspace_connectivity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get("service_name", "Workspace Core"),
            "manufacturer": "Osaühing X",
            "model": "Workspace Core",
        }

    @property
    def is_on(self):
        return bool(self.coordinator.heartbeat_state)

    @property
    def available(self):
        return True
