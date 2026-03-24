import time
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class XTemplateSensor(SensorEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self._attr_name = entry.data["name"]
        self._attr_unique_id = f"x_{entry.entry_id}"
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
            "value": self._value
        }


async def async_setup_entry(hass, entry, async_add_entities):
    sensor = XTemplateSensor(hass, entry)

    # salvesta referents API jaoks
    hass.data[DOMAIN]["entities"][entry.data["name"]] = sensor

    async_add_entities([sensor])