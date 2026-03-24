from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class XTemplateNodeSensor(SensorEntity):
    def __init__(self, hass, node):
        self.hass = hass
        self.node = node

        self._attr_name = f"{node} Status"
        self._attr_unique_id = f"x_{node.lower()}"
        self._attr_icon = "mdi:server-network"

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):
        return self.hass.data[DOMAIN]["connected"].get(self.node, False)

    @property
    def extra_state_attributes(self):
        data = self.hass.data[DOMAIN]
        return {
            "status": data["status"].get(self.node),
            "value": data["value"].get(self.node)
        }


async def async_setup_entry(hass, entry, async_add_entities):
    store = hass.data[DOMAIN]

    async def add_sensor(node):
        if node in store["sensors"]:
            return

        sensor = XTemplateNodeSensor(hass, node)
        store["sensors"][node] = sensor
        async_add_entities([sensor])

    store["add_sensor"] = add_sensor