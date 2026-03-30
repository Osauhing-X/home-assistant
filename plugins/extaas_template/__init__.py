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
        _LOGGER.error("Config entry has no data")
        return False

    host = entry.data.get("host")
    port = entry.data.get("port")

    if not host or not port:
        _LOGGER.error("Missing host/port")
        return False

    store = get_store(hass)
    stored = await store.async_load() or {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("runtime", {})
    hass.data[DOMAIN].setdefault("storage", {})

    # 👉 STORAGE (ainult JSON)
    hass.data[DOMAIN]["storage"][entry.entry_id] = stored.get(
        entry.entry_id, {"entities": {}}
    )

    # 👉 RUNTIME (MITTE SALVESTADA)
    runtime = hass.data[DOMAIN]["runtime"]

    if "session" not in runtime:
        runtime["session"] = aiohttp.ClientSession()

    coordinator = ExtaasCoordinator(hass, entry)

    runtime[entry.entry_id] = {
        "coordinator": coordinator
    }

    await async_setup_api(hass)

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "button"]
    )

    await coordinator.async_config_entry_first_refresh()

    _LOGGER.info("Extaas '%s' ready", entry.data.get("service_name"))
    return True