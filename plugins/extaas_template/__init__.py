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

    # Setup API endpoint
    await async_setup_api(hass)

    # **Seadista platvormid, et sensor.py/switch.py saaks async_add_entities**
    # Lisame "discovery_info", mida sensor.py ja switch.py ootavad
    discovery_info = {"entry_id": entry.entry_id}
    for platform in ["sensor", "switch"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    # Esimene värskendus
    await coordinator.async_config_entry_first_refresh()
    return True