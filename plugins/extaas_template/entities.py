import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_UPDATE

class Base(Entity):

    def __init__(self, hass, entry, key):
        self.hass = hass
        self.entry = entry
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def data(self):
        return self.hass.data[DOMAIN][self.entry.entry_id]["entities"].get(self.key, {})

    @property
    def available(self):
        coord = self.hass.data[DOMAIN][self.entry.entry_id]["coordinator"]
        return coord.data

    async def async_added_to_hass(self):
        async def update(eid, changed):
            if eid == self.entry.entry_id and self.key in changed:
                self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, update)
        )


class ExtaasSensor(Base):
    @property
    def state(self):
        return self.data.get("value")


class ExtaasSwitch(Base, SwitchEntity):

    @property
    def is_on(self):
        return self.data.get("value")

    async def async_turn_on(self, **kwargs):
        await self._send(True)

    async def async_turn_off(self, **kwargs):
        await self._send(False)

    async def _send(self, value):
        session = self.hass.data[DOMAIN]["session"]
        self.data["value"] = value
        self.async_write_ha_state()

        await session.post(
            f"http://{self.entry.data['host']}:{self.entry.data['port']}/update",
            json={self.key: value}
        )


class ExtaasButton(Base, ButtonEntity):

    async def async_press(self):
        session = self.hass.data[DOMAIN]["session"]

        await session.post(
            f"http://{self.entry.data['host']}:{self.entry.data['port']}/update",
            json={self.key: True}
        )