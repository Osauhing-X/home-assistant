from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import async_get_current_platform
from .const import DATA

SENSORS = {}

class XTemplateNodeSensor(SensorEntity):
    def __init__(self, node_name):
        self.node_name = node_name
        self._attr_name = f"{node_name} Status"
        self._attr_icon = "mdi:server-network"
        self._attr_unique_id = f"x_{node_name.lower()}"

    @property
    def native_value(self):
        return DATA["connected"].get(self.node_name, False)

    @property
    def extra_state_attributes(self):
        return {
            "status": DATA["status"].get(self.node_name),
            "value": DATA["value"].get(self.node_name)
        }

    @property
    def available(self):
        return True


async def async_add_sensor(hass, node_name):
    platform = await async_get_current_platform()
    sensor = XTemplateNodeSensor(node_name)
    SENSORS[node_name] = sensor
    platform.async_add_entities([sensor])