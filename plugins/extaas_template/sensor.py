from homeassistant.helpers.entity import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensors from config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    dynamic_entities = entry.data.get("dynamic_entities", [])

    entities = []

    # --- Heartbeat sensor (default) ---
    entities.append(ExtaasHeartbeatSensor(coordinator))

    # --- Dünaamilised sensorid ---
    for item in dynamic_entities:
        if item.get("type") == "sensor":
            entities.append(ExtaasDynamicSensor(coordinator, item))

    async_add_entities(entities, update_before_add=True)


class ExtaasHeartbeatSensor(CoordinatorEntity, SensorEntity):
    """Heartbeat sensor for each child device."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Heartbeat {coordinator.node_name}"
        self._attr_unique_id = f"{coordinator.host}:{coordinator.port}:heartbeat"
        self._attr_native_value = None

    @property
    def native_value(self):
        """Return current heartbeat state (True/False)."""
        return self.coordinator.heartbeat_state

    async def async_update(self):
        """Update heartbeat from coordinator."""
        await self.coordinator.async_refresh_heartbeat()
        self._attr_native_value = self.coordinator.heartbeat_state


class ExtaasDynamicSensor(CoordinatorEntity, SensorEntity):
    """Dynamic sensor entity based on coordinator.dynamic_entities."""

    def __init__(self, coordinator, item: dict):
        super().__init__(coordinator)
        self.item = item
        self._attr_name = item.get("name")
        self._attr_icon = item.get("icon")
        self._attr_unique_id = f"{coordinator.host}:{coordinator.port}:{item['name']}"
        self._attr_native_value = item.get("value", False)

    @property
    def native_value(self):
        """Return current value."""
        return self._attr_native_value

    async def async_update(self):
        """Update sensor value from coordinator."""
        # Koordinaator võib siin dünaamiliselt värskendada
        for entity in self.coordinator.dynamic_entities:
            if entity["name"] == self.item["name"]:
                self._attr_native_value = entity.get("value", False)
                break