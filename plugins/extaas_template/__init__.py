# __init__.py
from .coordinator import ExtaasCoordinator
from .devices_manager import ExtaasDevicesManager
from .const import DOMAIN
from .api import async_setup_api

async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    devices_manager = ExtaasDevicesManager(coordinator, entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "devices": devices_manager
    }

    # Setup API endpoint (POST Node serverist)
    await async_setup_api(hass)

    # Esimene andmete värskendus
    await coordinator.async_config_entry_first_refresh()
    return True