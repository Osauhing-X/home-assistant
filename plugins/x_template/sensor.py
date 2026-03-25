import time
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class XTemplateSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        name = entry.options.get("name") or entry.data["name"]

        self._attr_name = name
        self._attr_unique_id = f"x_{name.lower()}"
        self._attr_icon = "mdi:server-network"

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
        return {
            "status": self._status,
            "value": self._value,
            "host": self.entry.options.get("host") or self.entry.data.get("host"),
            "port": self.entry.options.get("port") or self.entry.data.get("port"),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self._attr_name,
            "manufacturer": "Extaas",
            "model": "Node Client",
        }


async def async_setup_entry(hass, entry, async_add_entities):
    sensor = XTemplateSensor(hass, entry)

    # link node name → sensor
    name = entry.options.get("name") or entry.data["name"]
    hass.data[DOMAIN]["entities"][name] = sensor

    async_add_entities([sensor])