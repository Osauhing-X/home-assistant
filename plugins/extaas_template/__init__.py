from homeassistant.core import HomeAssistant
import asyncio
from .coordinator import ExtaasCoordinator
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass, entry):
    """Set up the integration via config entry."""
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Salvesta coordinator ja node_data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # Forward setup to sensor platform
    hass.async_create_task(
    asyncio.gather(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"),
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
)
    return True


""" DELETE """
async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True