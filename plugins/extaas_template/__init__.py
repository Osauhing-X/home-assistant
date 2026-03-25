from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .store import get_store
from .coordinator import ExtaasCoordinator
from .api import ExtaasAPI

async def async_setup(hass: HomeAssistant, config: dict):
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True

async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # setup sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass, entry):
    """Reload entry when options updated."""
    await hass.config_entries.async_reload(entry.entry_id)