from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import SIGNAL_NEW_DATA

class ExtaasDynamicEntity(Entity):
    """Dynamic sensor/switch entity for Node"""

    def __init__(self, hass, entry_id, device_data, entity_data):
        self.hass = hass
        self.entry_id = entry_id
        self.device_data = device_data
        self.entity_data = entity_data

        self._attr_name = entity_data["name"]
        self._attr_unique_id = entity_data["unique_id"]
        self._attr_icon = entity_data.get("icon")
        self._attr_state = entity_data.get("value", False)
        self.entity_type = entity_data.get("type", "sensor")  # "sensor" või "switch"

    @property
    def state(self):
        return self._attr_state

    @property
    def is_on(self):
        if self.entity_type == "switch":
            return self._attr_state

    async def async_turn_on(self, **kwargs):
        if self.entity_type == "switch":
            await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        if self.entity_type == "switch":
            await self._async_toggle(False)

    async def _async_toggle(self, value: bool):
        """Send update to Node /update"""
        import aiohttp
        self._attr_state = value
        host = self.device_data["host"]
        port = self.device_data["port"]
        url = f"http://{host}:{port}/update"
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={self._attr_name: value})
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Subscribe to dispatcher for live updates"""
        async def _handle_update(*args):
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_NEW_DATA,
                _handle_update
            )
        )