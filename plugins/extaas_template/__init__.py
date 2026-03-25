from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import ExtaasCoordinator
from .const import DOMAIN
from .store import get_store
from .sensor import async_setup_entry as sensor_setup

async def async_setup(hass: HomeAssistant, config: dict):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = get_store(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # Setup sensor platform
    await sensor_setup(hass, entry, lambda entities: None)

    # OptionsFlow listener
    entry.async_on_unload(entry.add_update_listener(_update_listener))
    return True

async def _update_listener(hass, entry):
    """Reload integration on options update."""
    await hass.config_entries.async_reload(entry.entry_id)