from .const import DOMAIN
from .api import async_setup_api
from .store import get_store
from .devices_manager import ExtaasDevicesManager
from .coordinator import ExtaasCoordinator

async def async_setup_entry(hass, entry):
    """Setup HA entry: coordinator, devices, API, platforms."""

    # --- LOAD STORE ---
    store = get_store(hass)
    data = await store.async_load() or {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = data.get(entry.entry_id, {
        "devices": {}
    })

    # --- CORE OBJECTS ---
    coordinator = ExtaasCoordinator(
        hass,
        entry.entry_id,
        entry.data["host"],
        entry.data["port"]
    )
    devices = ExtaasDevicesManager(hass, entry)

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    hass.data[DOMAIN][entry.entry_id]["devices_manager"] = devices

    # --- API ---
    await async_setup_api(hass)

    # --- PLATFORMS ---
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])

    # --- RESTORE DYNAMIC ENTITIES (last saved state) ---
    await devices.restore_entities()

    # --- START HEARTBEAT ---
    await coordinator.async_config_entry_first_refresh()

    return True