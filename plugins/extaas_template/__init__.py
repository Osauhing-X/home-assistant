from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .devices import ExtaasDevices
from .const import DOMAIN
from .api import async_setup_api

async def async_setup_entry(hass: HomeAssistant, entry):
    """Setup entry with coordinator and devices."""

    coordinator = ExtaasCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    # Devices manager
    devices_manager = ExtaasDevices(hass, coordinator, entry.entry_id)
    hass.data[DOMAIN][entry.entry_id]["devices"] = devices_manager

    # HTTP API
    await async_setup_api(hass)

    # --- Platvormi register ---
    for platform in ["sensor", "switch"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    # Esmane refresh
    await coordinator.async_config_entry_first_refresh()
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    for platform in ["sensor", "switch"]:
        await hass.config_entries.async_forward_entry_unload(entry, platform)
    return True