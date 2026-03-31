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

    # --- Store management ---
    store = get_store(hass)
    stored_data = await store.async_load() or {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id].setdefault("entities", stored_data.get(entry.entry_id, {}).get("entities", {}))
    hass.data[DOMAIN][entry.entry_id].setdefault("runtime", {})

    # --- Shared HTTP session ---
    runtime = hass.data[DOMAIN][entry.entry_id]["runtime"]
    if "session" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["runtime"].setdefault("session", aiohttp.ClientSession())
    runtime["session"] = hass.data[DOMAIN]["runtime"]["session"]

    # --- Coordinator ---
    coordinator = ExtaasCoordinator(hass, entry)
    runtime["coordinator"] = coordinator

    # --- Setup API ---
    await async_setup_api(hass)

    # --- Forward to platforms ---
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "button"]
    )

    # --- Initial refresh ---
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.info("Extaas entry '%s' setup complete", service_name)
    return True