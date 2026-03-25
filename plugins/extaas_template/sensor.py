from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .helper import format_unique_id
from .store import get_store

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Heartbeat sensor
    async_add_entities([HeartbeatSensor(coordinator, entry)])

    # Dünaamilised sensorid Node poolt
    store = get_store(hass)
    for node, entities in store["entities"].items():
        for key in entities:
            async_add_entities([DynamicSensor(coordinator, entry, node, key)])

class HeartbeatSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"{entry.data.get('name')} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}_heartbeat"
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        return self.coordinator.data["connected"].get(self.entry.data.get("name"), False)

class DynamicSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, node, key):
        super().__init__(coordinator)
        self.entry = entry
        self.node = node
        self.key = key
        self._attr_name = f"{node} {key}"
        self._attr_unique_id = format_unique_id(f"{node}_{key}")
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        store = self.coordinator.data
        return store["entities"].get(self.node, {}).get(self.key)