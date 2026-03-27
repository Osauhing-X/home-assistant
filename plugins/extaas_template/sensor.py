from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .helpers import build_device_hierarchy
from .const import SIGNAL_NEW_DATA

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[entry.domain][entry.entry_id]["coordinator"]
    created = set()

    def add_entities():
        node_full = getattr(coordinator, "node_full", {})
        _, entities_cfg = build_device_hierarchy(entry, node_full)
        new_entities = []

        for cfg in entities_cfg:
            if cfg["platform"] != "sensor" or cfg["unique_id"] in created:
                continue

            key = cfg["key"]

            class DynSensor(CoordinatorEntity, SensorEntity):
                def __init__(self, coordinator):
                    super().__init__(coordinator)
                    self._key = key
                    self._attr_name = cfg["name"]
                    self._attr_unique_id = cfg["unique_id"]
                    self._attr_device_info = cfg["device_info"]
                    self.entity_description = cfg["entity_description"]

                @property
                def native_value(self):
                    return self.coordinator.node_data.get(self._key)

            new_entities.append(DynSensor(coordinator))
            created.add(cfg["unique_id"])

        if new_entities:
            async_add_entities(new_entities)

    add_entities()
    async_dispatcher_connect(hass, SIGNAL_NEW_DATA, lambda eid: eid == entry.entry_id and add_entities())