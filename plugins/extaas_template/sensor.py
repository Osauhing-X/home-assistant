from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


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
        return data.get("ok", False)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}

        return {
            "status": data.get("status"),
            "uptime": data.get("uptime"),
        }

    @property
    def available(self):
        # 👉 oluline – kui request failib, sensor läheb unavailable
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        cfg = self.entry.options or self.entry.data

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": cfg.get("name"),
            "manufacturer": "Extaas",
            "model": "Node Client",
        }


# ✅ setup jääb alles
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        XSensor(hass, entry, "heartbeat")
    ])