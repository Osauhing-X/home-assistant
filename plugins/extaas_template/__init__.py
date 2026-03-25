from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .api import ExtaasAPI
from .store import get_store
from .coordinator import ExtaasCoordinator


async def async_setup(hass: HomeAssistant, config: dict):
    get_store(hass)
    hass.http.register_view(ExtaasAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # ✅ FIX – nüüd defineeritud
    entry.async_on_unload(
        entry.add_update_listener(update_listener)
    )

    return True


# ✅ LISATUD
async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


# (optional, aga soovitan)
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok