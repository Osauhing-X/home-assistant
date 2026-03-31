from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

class BaseEntity(Entity):
    def __init__(self, hass, entry, key):
        self.hass = hass
        self.entry = entry
        self.key = key
        safe = f"{entry.data.get('service_name','extaas')}_{key}".lower().replace(" ", "_")
        self._attr_unique_id = safe
        self._attr_has_entity_name = True

    @property
    def data(self):
        return (
            self.hass.data[DOMAIN]
            .get("storage", {})
            .get(self.entry.entry_id, {})
            .get("entities", {})
            .get(self.key, {})
        )

    @property
    def name(self):
        return self.data.get("name", self.key)

    @property
    def icon(self):
        return self.data.get("icon")

    @property
    def available(self):
        return True

class ExtaasSensor(BaseEntity):
    @property
    def state(self):
        return self.data.get("value")

class ExtaasSwitch(BaseEntity, SwitchEntity):
    @property
    def is_on(self):
        return self.data.get("value")

    async def async_turn_on(self, **kwargs):
        await self._send(True)

    async def async_turn_off(self, **kwargs):
        await self._send(False)

    async def _send(self, value):
        runtime = self.hass.data[DOMAIN].setdefault("runtime", {})
        session = runtime.get("session")
        if not session:
            return
        self.data["value"] = value
        self.async_write_ha_state()
        await session.post(
            f"http://{self.entry.data['host']}:{self.entry.data['port']}/update",
            json={self.key: value}
        )

class ExtaasButton(BaseEntity, ButtonEntity):
    async def async_press(self):
        runtime = self.hass.data[DOMAIN].setdefault("runtime", {})
        session = runtime.get("session")
        if not session:
            return
        await session.post(
            f"http://{self.entry.data['host']}:{self.entry.data['port']}/update",
            json={self.key: True}
        )

def create_entity(hass, entry, e):
    typ = e.get("type")
    key = e.get("unique_id")
    if typ == "switch":
        return ExtaasSwitch(hass, entry, key)
    if typ == "button":
        return ExtaasButton(hass, entry, key)
    return ExtaasSensor(hass, entry, key)