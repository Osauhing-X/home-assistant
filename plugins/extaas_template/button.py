# button.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .entities import ExtaasButton
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("entities", {})
    buttons = [ExtaasButton(hass, entry, key) for key, e in data.items() if e.get("type")=="button"]
    if buttons:
        async_add_entities(buttons)