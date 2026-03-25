from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

class XTemplateNodeSensor(SensorEntity):
    def __init__(self, hass, node, device_info):
        self.hass = hass
        self.node = node
        self._device_info = device_info

        self._attr_name = f"{node} Heartbeat"
        self._attr_unique_id = f"x_{node.lower()}"
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        return self.hass.data[DOMAIN]["connected"].get(self.node, False)

    @property
    def extra_state_attributes(self):
        data = self.hass.data[DOMAIN]
        cfg = data.get("config", {})
        return {
            "status": data["status"].get(self.node),
            "value": data["value"].get(self.node),
            "last_seen": data["last_seen"].get(self.node),
            "host": cfg.get("host"),
            "port": cfg.get("port")
        }

    @property
    def device_info(self):
        return self._device_info


async def async_setup_entry(hass, entry, async_add_entities):
    store = hass.data[DOMAIN]

    async def add_sensor(node, device_info):
        if node in store["sensors"]:
            return
        sensor = XTemplateNodeSensor(hass, node, device_info)
        store["sensors"][node] = sensor
        async_add_entities([sensor])

    store["add_sensor"] = add_sensor