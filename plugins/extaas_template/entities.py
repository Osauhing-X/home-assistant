# entities.py
from homeassistant.helpers.entity import Entity
from .const import SIGNAL_NEW_DATA

class ExtaasDynamicEntity(Entity):
    """Dünaamiline sensor või switch entry -> device -> entity."""

    def __init__(self, coordinator, entry_id, service_name, entity_data):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.service_name = service_name
        self.entity_data = entity_data

        self._attr_name = entity_data["name"]
        self._attr_unique_id = f"{entry_id}:{service_name}:{entity_data['name']}"
        self._attr_icon = entity_data.get("icon")
        self._attr_state = entity_data.get("value", False)
        self.entity_type = entity_data.get("type", "sensor")  # "sensor" või "switch"

        # device_id on service_device grupp
        self._attr_device_id = f"{entry_id}_{service_name}"

    @property
    def is_on(self):
        return self._attr_state

    async def async_turn_on(self, **kwargs):
        if self.entity_type == "switch":
            await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        if self.entity_type == "switch":
            await self._async_toggle(False)

    async def _async_toggle(self, value: bool):
        self._attr_state = value
        item = {
            "host": self.coordinator.host,
            "port": self.coordinator.port,
            "name": self._attr_name,
            "value": value,
        }
        self.coordinator.add_to_todo(item)
        self.async_write_ha_state()