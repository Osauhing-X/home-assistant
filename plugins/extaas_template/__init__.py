from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import ExtaasCoordinator
from .store import get_store


async def async_setup(hass: HomeAssistant, config: dict):
    # store init
    get_store(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Coordinator
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # Setup sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Listen entry updates
    async def update_listener(hass, entry):
        await hass.config_entries.async_reload(entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True