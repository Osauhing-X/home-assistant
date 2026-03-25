from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

class XTemplateNodeSensor(SensorEntity):
    def __init__(self, hass, node, entry):
        self.hass = hass
        self.node = node
        self.entry = entry

        self._attr_name = f"{node} Heartbeat"
        self._attr_unique_id = f"x_{node.lower()}"
        self._attr_icon = "mdi:server-network"

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
        cfg = self.entry.data
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "entry_type": "service",  # see võimaldab dashboardil kuvada
            "name": cfg["name"],
            "manufacturer": "Extaas",
            "model": "Node Client",
            "configuration_url": f"http://{cfg['host']}:{cfg['port']}"
        }


async def async_setup_entry(hass, entry, async_add_entities):
    store = hass.data[DOMAIN]

    async def add_sensor(node):
        if node in store["sensors"]:
            return
        sensor = XTemplateNodeSensor(hass, node, entry)
        store["sensors"][node] = sensor
        async_add_entities([sensor])

    store["add_sensor"] = add_sensor