from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

class XTemplateNodeSensor(SensorEntity):
    def __init__(self, hass, node, device_info):
        self.hass = hass
        self.node = node
        self.device_info_data = device_info

        self._attr_name = f"{node} Heartbeat"
        self._attr_unique_id = f"x_{node.lower()}"
        self._attr_icon = "mdi:heartbeat"

    @property
    def native_value(self):
        return self.hass.data[DOMAIN]["connected"].get(self.node, False)

    @property
    def extra_state_attributes(self):
        data = self.hass.data[DOMAIN]
        return {
            "status": data["status"].get(self.node),
            "value": data["value"].get(self.node),
            "last_seen": data["last_seen"].get(self.node)
        }

    @property
    def device_info(self):
        """Tagab seadme info, et ilmuks Devices & Services lehele"""
        return self.device_info_data