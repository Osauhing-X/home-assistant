from .const import DOMAIN
from .coordinator import ExtaasCoordinator
from .api import async_setup_api

async def async_setup_entry(hass, entry):
    """Setup integration entry."""

    coordinator = ExtaasCoordinator(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # API endpoint
    await async_setup_api(hass)

    # 🔥 ÕIGE viis platformite laadimiseks
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "switch"]
    )

    return True