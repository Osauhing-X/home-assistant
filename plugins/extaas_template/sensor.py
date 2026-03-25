from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]

    coordinator = data["coordinator"]
    store = hass.data[DOMAIN]["store"]

    entities = []

    # ❤️ Heartbeat seadmena
    heartbeat = HeartbeatSensor(coordinator, entry)
    entities.append(heartbeat)
    data["entities"]["heartbeat"] = heartbeat

    async_add_entities(entities)

    # Funktsioon dynaamiliste sensorite lisamiseks
    def update_entities(node):
        node_data = store.get_node(node)
        new_entities = []

        for key, value in node_data.items():
            entity_id = f"{node}_{key}"

            if entity_id not in data["entities"]:
                ent = DynamicSensor(coordinator, entry, node, key, value)
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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data["name"],
            manufacturer="Extaas",
            model="Heartbeat",
            configuration_url=f"http://{entry.data['host']}:{entry.data['port']}"
        )
        self._icon = "mdi:server"

    @property
    def native_value(self):
        return self.coordinator.data.get("ok", False)

    @property
    def icon(self):
        return self._icon


class DynamicSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, node, key, value):
        super().__init__(coordinator)
        self.node = node
        self.key = key
        self.value = value

        self._attr_name = f"{node} {key}"
        self._attr_unique_id = f"{entry.entry_id}_{node}_{key}"

        # seadme info (iga sensor eraldi seadmena)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{node}")},
            name=node,
            manufacturer="Extaas",
            model="Dynamic Sensor",
            configuration_url=f"http://{entry.data['host']}:{entry.data['port']}"
        )

        # ikooni seadistamine
        if key.lower() == "heartbeat":
            self._icon = "mdi:server"
        else:
            self._icon = value.get("icon", "mdi:checkbox-blank-outline") if isinstance(value, dict) else "mdi:checkbox-blank-outline"

    @property
    def native_value(self):
        store = self.hass.data[DOMAIN]["store"]
        return store.get_node(self.node).get(self.key)

    @property
    def icon(self):
        return self._icon