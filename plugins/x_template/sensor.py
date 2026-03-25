import time
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class XTemplateSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._node_name = entry.data["name"]

        self._attr_name = self._node_name
        self._attr_unique_id = f"x_{entry.entry_id}"
        self._attr_icon = "mdi:server-network"
        self._attr_has_entity_name = True

        self._connected = False
        self._value = None
        self._status = "offline"
        self._last_seen = 0

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):
        return self._connected

    @property
    def extra_state_attributes(self):
        host = self.entry.data.get("host")
        port = self.entry.data.get("port")

        return {
            "status": self._status,
            "value": self._value,
            "host": host,
            "port": port,
            "last_seen": self._last_seen
        }

    @property
    def device_info(self):
        host = self.entry.data.get("host")
        port = self.entry.data.get("port")

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self._node_name,
            "manufacturer": "Extaas",
            "model": "Node Client",

            # 🔥 SEE teeb "Visit" nupu UI-s
            "configuration_url": f"http://{host}:{port}" if host else None,
        }


async def async_setup_entry(hass, entry, async_add_entities):
    sensor = XTemplateSensor(hass, entry)

    # 🔥 ÕIGE mapping
    hass.data[DOMAIN]["entities"][entry.entry_id] = sensor
    hass.data[DOMAIN]["nodes"][entry.data["name"]] = entry.entry_id

    async_add_entities([sensor])