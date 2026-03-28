import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity

def create_entity(hass, entry, device, data):
    if data["type"] == "switch":
        return ExtaasSwitch(hass, entry, device, data)
    return ExtaasSensor(hass, entry, device, data)


class Base(Entity):

    def __init__(self, hass, entry, device, data):
        self.hass = hass
        self.entry = entry
        self.device = device
        self.data = data

        self._attr_name = data["name"]
        self._attr_unique_id = data["unique_id"]
        self._attr_icon = data.get("icon")

    @property
    def state(self):
        return self.data.get("value")


class ExtaasSensor(Base):
    pass


class ExtaasSwitch(Base, SwitchEntity):

    @property
    def is_on(self):
        return self.data.get("value")

    async def async_turn_on(self, **kwargs):
        await self._send(True)

    async def async_turn_off(self, **kwargs):
        await self._send(False)

    async def _send(self, value):
        """Send switch update to Node and immediately update local state"""
        self.data["value"] = value
        self.async_write_ha_state()

        url = f"http://{self.device['host']}:{self.device['port']}/update"
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={self._attr_name: value})