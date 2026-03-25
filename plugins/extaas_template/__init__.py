from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .api import ExtaasAPI
from .store import get_store
from .sensor import setup_heartbeat_sensor  # <- muudetud nimetus

async def async_setup(hass: HomeAssistant, config: dict):
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Setup heartbeat sensor ainult
    await setup_heartbeat_sensor(hass, entry)
    return True