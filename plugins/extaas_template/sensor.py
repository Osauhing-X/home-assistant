from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]

    coordinator = data["coordinator"]
    store = hass.data[DOMAIN]["store"]

    entities = []

    # ALWAYS create heartbeat
    heartbeat = HeartbeatSensor(coordinator, entry)
    entities.append(heartbeat)

    data["entities"]["heartbeat"] = heartbeat

    async_add_entities(entities)

    def update_entities(node):
        node_data = store.get_node(node)

        new_entities = []
        for key in node_data:
            entity_id = f"{node}_{key}"

            if entity_id not in data["entities"]:
                ent = DynamicSensor(coordinator, entry, node, key)
                data["entities"][entity_id] = ent
                new_entities.append(ent)

        if new_entities:
            async_add_entities(new_entities)

    hass.data[DOMAIN]["update_entities"] = update_entities


class HeartbeatSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} Heartbeat"
        self._attr_unique_id = f"{entry.entry_id}_heartbeat"

    @property
    def native_value(self):
        return self.coordinator.data.get("ok", False)


class DynamicSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, node, key):
        super().__init__(coordinator)
        self.node = node
        self.key = key

        self._attr_name = f"{node} {key}"
        self._attr_unique_id = f"{entry.entry_id}_{node}_{key}"

    @property
    def native_value(self):
        store = self.hass.data[DOMAIN]["store"]
        return store.get_node(self.node).get(self.key)