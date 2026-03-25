from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .store import get_store

class XSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, hass, entry, node):
        self.hass = hass
        self.entry = entry
        self.node = node

        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        super().__init__(coordinator)

        self._attr_name = f"{node} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}_{node}"
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("status") == "online"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return data

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([XSensor(hass, entry, "heartbeat")])