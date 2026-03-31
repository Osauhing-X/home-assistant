# switch.py
from .entities import ExtaasSwitch
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    entities = [ExtaasSwitch(hass, entry, key) for key in data if data[key]["type"] == "switch"]
    async_add_entities(entities)