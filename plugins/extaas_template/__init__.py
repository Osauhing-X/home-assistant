from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .devices import ExtaasDevices
from .const import DOMAIN
from .api import async_setup_api

async def async_setup_entry(hass: HomeAssistant, entry):
    """Setup entry with coordinator and devices."""

    coordinator = ExtaasCoordinator(hass, entry)
    devices_manager = ExtaasDevices(hass, coordinator, entry.entry_id)

    # Salvesta coordinator ja devices entry alla
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "devices": devices_manager,
        "platforms": {}  # callbackid platvormidele
    }

    # HTTP API
    await async_setup_api(hass)

    # --- Universaalne platvorm register --- #
    # Callback async_add_entities salvestatakse devices_managerisse
    async def async_add_entities_callback(entities):
        # Selle callbacki kaudu lisab devices_manager entity-d HA-sse
        from homeassistant.helpers.entity_platform import async_add_entities
        async_add_entities(entities)

    # Registreeri platvormid seadistuse käigus
    devices_manager.register_platform("sensor", async_add_entities_callback)
    devices_manager.register_platform("switch", async_add_entities_callback)

    # Esmane refresh
    await coordinator.async_config_entry_first_refresh()
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True