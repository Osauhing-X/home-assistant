from .entities import ExtaasDynamicEntity
from .const import SIGNAL_NEW_DATA
from homeassistant.helpers.dispatcher import async_dispatcher_connect

class ExtaasDevicesManager:
    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.entities = []

    def setup_entities(self, async_add_entities, entity_type=None):
        entities = []

        # Heartbeat sensor
        if entity_type == "sensor":
            entities.append(ExtaasDynamicEntity(
                self.coordinator, self.entry_id, self.coordinator.node_name,
                {"name": f"{self.coordinator.node_name} Heartbeat",
                 "type": "sensor",
                 "value": self.coordinator.heartbeat_state}
            ))

        # Dünaamilised entityd
        for e in self.coordinator.dynamic_entities:
            if entity_type == "switch" and e.get("type") == "switch":
                entities.append(ExtaasDynamicEntity(self.coordinator, self.entry_id, self.coordinator.node_name, e))
            elif entity_type == "sensor" and e.get("type") != "switch":
                entities.append(ExtaasDynamicEntity(self.coordinator, self.entry_id, self.coordinator.node_name, e))

        # Kuula dispatcherit
        for entity in entities:
            async_dispatcher_connect(self.coordinator.hass, SIGNAL_NEW_DATA, entity.async_write_ha_state)

        async_add_entities(entities)
        self.entities.extend(entities)