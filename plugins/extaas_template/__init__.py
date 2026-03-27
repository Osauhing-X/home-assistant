from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass, entry):
    """Setup entry for Extaas integration."""
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])
    return True

async def async_unload_entry(hass, entry):
    """Unload entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True