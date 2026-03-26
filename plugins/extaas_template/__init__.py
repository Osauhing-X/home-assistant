from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import ExtaasDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry):
    coordinator = ExtaasDataUpdateCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    # Setup sensors
    from .sensor import async_setup_entry
    await async_setup_entry(hass, entry, coordinator)

    return True