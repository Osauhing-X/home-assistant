from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .api import ExtaasAPI
from .store import get_store


async def async_setup(hass: HomeAssistant, config: dict):
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # reload support (OptionsFlow)
    entry.async_on_unload(
        entry.add_update_listener(update_listener)
    )

    return True


async def update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)