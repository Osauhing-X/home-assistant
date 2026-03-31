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
        return False

    host = entry.data.get("host")
    port = entry.data.get("port")

    if not host or not port:
        return False

    # -------------------------
    # INIT DOMAIN STRUCTURE
    # -------------------------
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("_runtime", {})

    # -------------------------
    # LOAD PERSISTED DATA
    # -------------------------
    store = get_store(hass)
    stored = await store.async_load() or {}

    hass.data[DOMAIN][entry.entry_id] = stored.get(
        entry.entry_id,
        {"entities": {}}
    )

    # -------------------------
    # SHARED SESSION (runtime only)
    # -------------------------
    runtime = hass.data[DOMAIN]["_runtime"]

    if "session" not in runtime:
        runtime["session"] = aiohttp.ClientSession()

        async def close_session(event):
            await runtime["session"].close()

        hass.bus.async_listen_once("homeassistant_stop", close_session)

    # -------------------------
    # COORDINATOR (runtime only)
    # -------------------------
    coordinator = ExtaasCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    # -------------------------
    # API (register once)
    # -------------------------
    if not runtime.get("api_registered"):
        await async_setup_api(hass)
        runtime["api_registered"] = True

    # -------------------------
    # PLATFORMS
    # -------------------------
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "button"]
    )

    await coordinator.async_config_entry_first_refresh()

    return True