from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .store import get_store
from .coordinator import ExtaasCoordinator
from .sensor import async_setup_entry as sensor_async_setup

async def async_setup(hass, config):
    get_store(hass)
    return True

async def async_setup_entry(hass, entry: ConfigEntry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await sensor_async_setup(hass, entry, lambda entities=None: None)

    entry.async_on_unload(
        entry.add_update_listener(_update_listener)
    )
    return True

async def _update_listener(hass, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)