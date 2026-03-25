from .coordinator import ExtaasCoordinator
from .const import DOMAIN
from .store import get_store
from .sensor import XSensor

async def async_setup(hass, config):
    get_store(hass)
    hass.http.register_view(__import__("custom_components.extaas_template.api").ExtaasAPI)
    return True

async def async_setup_entry(hass, entry):
    """Setup entry koos heartbeat + coordinator."""
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    # Heartbeat sensor
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    # Update listener
    entry.async_on_unload(
        entry.add_update_listener(update_listener)
    )
    return True

async def update_listener(hass, entry):
    """Reload entry kui options muutuvad."""
    await hass.config_entries.async_reload(entry.entry_id)