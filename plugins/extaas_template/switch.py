# switch.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .entities import ExtaasSwitch
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("entities", {})
    switches = [ExtaasSwitch(hass, entry, key) for key, e in data.items() if e.get("type")=="switch"]
    if switches:
        async_add_entities(switches)