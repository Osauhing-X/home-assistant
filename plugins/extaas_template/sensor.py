from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .store import get_store

class HeartbeatSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_name = f"{entry.data['name']} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}_heartbeat"

    @property
    def native_value(self):
        store = get_store(self.hass)
        return store["connected"].get("heartbeat", False)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self.entry.data["name"],
            "manufacturer": "Extaas",
            "model": "Node Client",
        }

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([HeartbeatSensor(hass, entry)])