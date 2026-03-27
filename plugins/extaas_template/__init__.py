from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .store import get_store
from .api import ExtaasAPI

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup integration and register API."""
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True