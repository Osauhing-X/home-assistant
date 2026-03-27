from .coordinator import ExtaasCoordinator
from .devices_manager import ExtaasDevicesManager
from .const import DOMAIN
from .api import async_setup_api

async def async_setup_entry(hass, entry):
    """Setup entry: coordinator, devices manager, API, sensorid ja switchid."""

    # --- Koordinaator ---
    coordinator = ExtaasCoordinator(hass, entry)

    # --- Devices manager ---
    devices_manager = ExtaasDevicesManager(coordinator, entry.entry_id)

    # --- Salvesta entry data ---
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "devices": devices_manager
    }

    # --- API endpoint ---
    await async_setup_api(hass)

    # --- Platvormid ---
    # See kutsub sensor.py ja switch.py async_setup_entry
    for platform in ["sensor", "switch"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(entry, platform)
        )

    # --- Esimene värskendus ---
    await coordinator.async_config_entry_first_refresh()

    return True