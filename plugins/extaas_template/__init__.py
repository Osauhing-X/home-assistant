from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .const import DOMAIN, SIGNAL_NEW_DATA
from .api import async_setup_api

async def async_setup_entry(hass: HomeAssistant, entry):
    """Setup entry and coordinator."""
    host = entry.data["host"]
    port = entry.data["port"]
    node_name = entry.data.get("hostname", host)

    # Loome koordinaatori entry alla
    coordinator = ExtaasCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    # Registreeri HTTP API
    await async_setup_api(hass)

    # Refresh esmakordselt
    await coordinator.async_config_entry_first_refresh()
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True