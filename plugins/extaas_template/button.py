# button.py
from .entities import ExtaasButton
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    entities = [ExtaasButton(hass, entry, key) for key in data if data[key]["type"] == "button"]
    async_add_entities(entities)