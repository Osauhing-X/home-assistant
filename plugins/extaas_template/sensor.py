from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
from .store import get_store


class XSensor(SensorEntity):

    def __init__(self, hass, entry, node):
        self.hass = hass
        self.entry = entry
        self.node = node

        self._attr_name = f"{node} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}_{node}"
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        store = get_store(self.hass)
        return store["connected"].get(self.node, False)

    @property
    def extra_state_attributes(self):
        store = get_store(self.hass)
        cfg = self.entry.options or self.entry.data

        return {
            "status": store["status"].get(self.node),
            "value": store["value"].get(self.node),
            "last_seen": store["last_seen"].get(self.node),
            "host": cfg.get("host"),
            "port": cfg.get("port"),
        }

    @property
    def device_info(self):
        cfg = self.entry.options or self.entry.data

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": cfg.get("name"),
            "manufacturer": "Extaas",
            "model": "Node Client",
        }


async def async_setup_entry(hass, entry, async_add_entities):
    # 👇 CRITICAL – heartbeat kohe olemas
    async_add_entities([XSensor(hass, entry, "heartbeat")])