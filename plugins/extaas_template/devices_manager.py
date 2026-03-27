from .entities import ExtaasDynamicEntity
from .const import SIGNAL_NEW_DATA

class ExtaasDevicesManager:
    """Haldab HA entitysid coordinatori kaudu."""

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.entities = []

    def setup_entities(self, async_add_entities, entity_type=None):
        """Loo kõik switchid/sensorid + Heartbeat."""
        entities = []

        # Heartbeat sensor
        entities.append(ExtaasDynamicEntity(self.coordinator, self.entry_id,
                                             self.coordinator.node_name,
                                             {"name": f"{self.coordinator.node_name} Heartbeat",
                                              "type": "sensor",
                                              "value": self.coordinator.heartbeat_state}))

        # Dünaamilised entiteedid
        for e in self.coordinator.dynamic_entities:
            if entity_type == "switch" and e.get("type") == "switch":
                entities.append(ExtaasDynamicEntity(self.coordinator, self.entry_id,
                                                     self.coordinator.node_name, e))
            elif entity_type == "sensor" and e.get("type") != "switch":
                entities.append(ExtaasDynamicEntity(self.coordinator, self.entry_id,
                                                     self.coordinator.node_name, e))

        async_add_entities(entities)
        self.entities.extend(entities)