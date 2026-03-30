from .entities import ExtaasButton
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    storage = hass.data[DOMAIN]["storage"]
    entry_data = storage.get(entry.entry_id, {})

    entities = entry_data.get("entities", {})

    async_add_entities([
        ExtaasButton(hass, entry, k)
        for k, v in entities.items()
        if v.get("type") == "button"
    ])