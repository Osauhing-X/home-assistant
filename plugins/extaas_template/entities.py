from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SIGNAL_UPDATE


class BaseEntity(Entity):
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
        # 👉 võiks siduda heartbeatiga tulevikus
        return True

    async def async_added_to_hass(self):
        async def update(eid, changed):
            if eid == self.entry.entry_id and self.key in changed:
                self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, update)
        )


# -------------------------
# SENSOR
# -------------------------
class ExtaasSensor(BaseEntity):
    @property
    def state(self):
        return self.data.get("value")


# -------------------------
# SWITCH
# -------------------------
class ExtaasSwitch(BaseEntity, SwitchEntity):
    @property
    def is_on(self):
        return self.data.get("value")

    async def async_turn_on(self, **kwargs):
        await self._send(True)

    async def async_turn_off(self, **kwargs):
        await self._send(False)

    async def _send(self, value):
        session = self.hass.data[DOMAIN]["_runtime"]["session"]

        url = f"http://{self.entry.data['host']}:{self.entry.data['port']}/update"

        # 👉 optimistlik UI update (OK)
        self.data["value"] = value
        self.async_write_ha_state()

        try:
            async with session.post(url, json={self.key: value}, timeout=10) as resp:
                if resp.status != 200:
                    raise HomeAssistantError(
                        f"Device returned HTTP {resp.status}"
                    )
        except Exception as err:
            # 👉 revert state kui request failib
            self.data["value"] = not value
            self.async_write_ha_state()

            raise HomeAssistantError(f"Failed to send switch update: {err}") from err


# -------------------------
# BUTTON
# -------------------------
class ExtaasButton(BaseEntity, ButtonEntity):
    async def async_press(self):
        session = self.hass.data[DOMAIN]["_runtime"]["session"]

        url = f"http://{self.entry.data['host']}:{self.entry.data['port']}/update"

        try:
            async with session.post(url, json={self.key: True}, timeout=10) as resp:
                if resp.status != 200:
                    raise HomeAssistantError(
                        f"Device returned HTTP {resp.status}"
                    )
        except Exception as err:
            raise HomeAssistantError(f"Failed to press button: {err}") from err