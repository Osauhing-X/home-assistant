from .const import DOMAIN
from .coordinator import ExtaasCoordinator
from .store import ExtaasStore
from .api import async_setup_api

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["store"] = ExtaasStore()
    await async_setup_api(hass)
    return True

async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "entities": {}
    }
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok