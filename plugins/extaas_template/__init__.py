import aiohttp
import logging
from .const import DOMAIN
from .store import get_store
from .api import async_setup_api
from .coordinator import ExtaasCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Setup a config entry."""
    if not entry.data:
        _LOGGER.error("Config entry has no data, skipping setup")
        return False

    host = entry.data.get("host")
    port = entry.data.get("port")
    service_name = entry.data.get("service_name", "Extaas Device")

    if not host or not port:
        _LOGGER.error("Config entry missing host or port, skipping setup")
        return False

    # Store management
    store = get_store(hass)
    data = await store.async_load() or {}
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("storage", {})
    hass.data[DOMAIN].setdefault("runtime", {})

    hass.data[DOMAIN]["storage"].setdefault(entry.entry_id, {"entities": {}})

    # Shared HTTP session
    if "session" not in hass.data[DOMAIN]["runtime"]:
        hass.data[DOMAIN]["runtime"]["session"] = aiohttp.ClientSession()

    # Coordinator
    coordinator = ExtaasCoordinator(hass, entry)
    hass.data[DOMAIN]["runtime"][entry.entry_id] = {"coordinator": coordinator}

    # Setup API
    await async_setup_api(hass)

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "button"]
    )

    # Initial refresh
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.info("Extaas entry '%s' setup complete", service_name)
    return True