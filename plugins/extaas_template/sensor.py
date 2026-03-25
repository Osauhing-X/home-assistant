import logging
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HeartbeatSensor(SensorEntity):
    def __init__(self, entry):
        self.entry = entry

        name = entry.data["name"]

        self._attr_name = f"{name} Heartbeat"
        self._attr_unique_id = f"x_{entry.entry_id}"
        self._attr_icon = "mdi:heart-pulse"

        self._state = False

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        host = self.entry.data.get("host")
        port = self.entry.data.get("port")

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self.entry.data["name"],
            "manufacturer": "Extaas",
            "model": "Node Client",
            "configuration_url": f"http://{host}:{port}"
        }


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.warning("SENSOR LOADED")

    sensor = HeartbeatSensor(entry)

    async_add_entities([sensor])