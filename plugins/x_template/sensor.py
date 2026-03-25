import time
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class XTemplateSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._node_name = entry.options.get("name") or entry.data["name"]

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
        host = self.entry.options.get("host") or self.entry.data.get("host")
        port = self.entry.options.get("port") or self.entry.data.get("port")

        return {
            "status": self._status,
            "value": self._value,
            "host": host,
            "port": port,
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

            # 🔥 IP kuvamine
            "connections": {("ip", host)} if host else set(),

            # 🔥 port kuvamine
            "sw_version": f"Port {port}" if port else None,
        }


async def async_setup_entry(hass, entry, async_add_entities):
    sensor = XTemplateSensor(hass, entry)

    # 🔥 entry_id põhine mapping (ÕIGE)
    hass.data[DOMAIN]["entities"][entry.entry_id] = sensor

    async_add_entities([sensor])