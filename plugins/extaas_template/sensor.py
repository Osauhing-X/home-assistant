from .entities import ExtaasSensor
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    entities = [ExtaasSensor(hass, entry, key) for key in data if data[key]["type"] == "sensor"]
    async_add_entities(entities)