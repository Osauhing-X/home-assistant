# switch.py
from .entities import ExtaasSwitch
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    async_add_entities([ExtaasSwitch(hass, entry, k) for k, v in data.items() if v.get("type")=="switch"])