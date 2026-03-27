from .coordinator import ExtaasCoordinator
from .devices_manager import ExtaasDevicesManager

async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    devices_manager = ExtaasDevicesManager(hass, coordinator, entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "devices": devices_manager
    }

    await async_setup_api(hass)

    # Forward platvormidele
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )

    await coordinator.async_config_entry_first_refresh()
    return True