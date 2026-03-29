import aiohttp
from .const import DOMAIN
from .store import get_store
from .api import async_setup_api
from .coordinator import ExtaasCoordinator

async def async_setup_entry(hass, entry):
    store = get_store(hass)
    data = await store.async_load() or {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = data.get(entry.entry_id, {
        "entities": {}
    })

    # shared HTTP session
    hass.data[DOMAIN]["session"] = aiohttp.ClientSession()

    coordinator = ExtaasCoordinator(
        hass,
        entry.data["host"],
        entry.data["port"]
    )

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    await async_setup_api(hass)

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch", "button"]
    )

    await coordinator.async_config_entry_first_refresh()

    return True