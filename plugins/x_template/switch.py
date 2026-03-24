from homeassistant.components.switch import SwitchEntity
import requests

API_URL = "http://HOST_IP:3000/switch"  # <-- muuda

class XTemplateSwitch(SwitchEntity):
    def __init__(self):
        self._attr_name = "X Template Switch"
        self._attr_is_on = False
        self._attr_icon = "mdi:power"

    def turn_on(self, **kwargs):
        self._attr_is_on = True
        try:
            requests.post(API_URL, json={"state": True})
        except Exception:
            pass

    def turn_off(self, **kwargs):
        self._attr_is_on = False
        try:
            requests.post(API_URL, json={"state": False})
        except Exception:
            pass


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([XTemplateSwitch()])