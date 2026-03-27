from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .devices import ExtaasDevices
from .const import DOMAIN, SIGNAL_NEW_DATA
from .api import async_setup_api

async def async_setup_entry(hass: HomeAssistant, entry):
    """Setup entry with coordinator and devices."""
    # Loome koordinaatori
    coordinator = ExtaasCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    # Loome devices manager entry alla
    devices_manager = ExtaasDevices(hass, coordinator, entry.entry_id)
    hass.data[DOMAIN][entry.entry_id]["devices"] = devices_manager

    # Registreeri HTTP API
    await async_setup_api(hass)

    # Esmane refresh
    await coordinator.async_config_entry_first_refresh()
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True