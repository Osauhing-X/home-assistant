from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .api import ExtaasAPI
from .store import get_store
from .sensor import async_setup_entry

async def async_setup(hass: HomeAssistant, config: dict):
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Setup heartbeat sensor
    await async_setup_entry(hass, entry, lambda sensors=None: None)
    return True