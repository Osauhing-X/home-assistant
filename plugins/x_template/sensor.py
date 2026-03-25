import time
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class HeartbeatSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._node_name = entry.options.get("name") or entry.data["name"]

        # ❗ EI kasuta has_entity_name
        self._attr_name = f"{self._node_name} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}"
        self._attr_icon = "mdi:heart-pulse"

        self._connected = False
        self._value = None
        self._last_seen = 0

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):
        return self._connected

    @property
    def extra_state_attributes(self):
        host = self.entry.options.get("host") or self.entry.data.get("host")
        port = self.entry.options.get("port") or self.entry.data.get("port")

        return {
            "value": self._value,
            "host": host,
            "port": port,
            "last_seen": self._last_seen
        }

    @property
    def device_info(self):
        host = self.entry.options.get("host") or self.entry.data.get("host")
        port = self.entry.options.get("port") or self.entry.data.get("port")

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self._node_name,
            "manufacturer": "Extaas",
            "model": "Node Client",

            # 👇 SEE on ainus õige koht linkimiseks
            "configuration_url": f"http://{host}:{port}" if host else None,
        }


async def async_setup_entry(hass, entry, async_add_entities):
    sensor = HeartbeatSensor(hass, entry)

    hass.data[DOMAIN]["entities"][entry.entry_id] = sensor
    hass.data[DOMAIN]["nodes"][entry.data["name"]] = entry.entry_id

    async_add_entities([sensor])