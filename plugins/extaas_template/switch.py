from homeassistant.helpers.entity import ToggleEntity
import aiohttp

class ExtaasSwitch(ToggleEntity):
    """Dünaamiline switch entity"""

    def __init__(self, coordinator, device_info, switch_name):
        self.coordinator = coordinator
        self._device_info = device_info
        self._name = switch_name
        self._state = False

        self._attr_unique_id = f"{coordinator.node_name}_{switch_name}"
        self._attr_name = f"{coordinator.node_name} {switch_name}"

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return self._device_info

    async def async_turn_on(self, **kwargs):
        await self._update_node(True)

    async def async_turn_off(self, **kwargs):
        await self._update_node(False)

    async def _update_node(self, value):
        url = f"http://{self.coordinator.host}:{self.coordinator.port}/update"
        self._state = value
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={self._name: value})