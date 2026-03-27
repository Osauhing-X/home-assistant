from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .store import get_store
import time

class XSensor(CoordinatorEntity, SensorEntity):
    """Heartbeat sensor."""

    def __init__(self, hass, node, key=None):
        """
        node: Node nimi
        key: Kui key==None -> heartbeat sensor
        """
        self.hass = hass
        self.node = node
        self.key = key  # null tähendab heartbeat sensor
        super().__init__(None)  # ilma coordinator'ita, push based

        self._attr_name = f"{node} {key}" if key else f"{node} Heartbeat"
        self._attr_unique_id = f"x_{node}" if not key else f"x_{node}_{key}"
        self._attr_icon = "mdi:server-network" if not key else "mdi:server"

    @property
    def native_value(self):
        store = get_store(self.hass)
        if not self.key:
            # heartbeat sensor
            node_data = store["nodes"].get(self.node, {})
            last_seen = node_data.get("last_seen")
            if not last_seen:
                return False
            if time.time() - last_seen > 20:  # heartbeat timeout
                return False
            return True
        else:
            # dynaamiline key sensor
            node_entities = store["entities"].get(self.node, {})
            data = node_entities.get(self.key, {}).get("value")
            return data

    @property
    def extra_state_attributes(self):
        if not self.key:
            return {}
        store = get_store(self.hass)
        node_entities = store["entities"].get(self.node, {})
        entity_data = node_entities.get(self.key, {})
        return {
            "node": self.node,
            "key": self.key,
            "last_updated": entity_data.get("last_updated"),
            "type": type(entity_data.get("value")).__name__ if "value" in entity_data else None
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.node)},
            "name": f"Extaas {self.node}",
            "manufacturer": "Extaas",
            "model": "Node Client",
        }