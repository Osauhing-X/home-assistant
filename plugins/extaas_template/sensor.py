from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .helper import build_device_hierarchy

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[entry.domain][entry.entry_id]["coordinator"]
    _, _, entities_cfg = build_device_hierarchy(entry, coordinator.node_data)

    sensors = []

    for cfg in entities_cfg:
        if hasattr(cfg["entity_description"], "icon") and "Sensor" in str(type(cfg["entity_description"])):
            class DynSensor(CoordinatorEntity, SensorEntity):
                def __init__(self, coordinator):
                    super().__init__(coordinator)
                    self._key = cfg["entity_description"].key
                    self._attr_name = cfg["name"]
                    self._attr_unique_id = cfg["unique_id"]
                    self._attr_device_info = cfg["device_info"]
                    self.entity_description = cfg["entity_description"]

                @property
                def native_value(self):
                    return self.coordinator.node_data.get(self._key)

            sensors.append(DynSensor(coordinator))

    async_add_entities(sensors, True)