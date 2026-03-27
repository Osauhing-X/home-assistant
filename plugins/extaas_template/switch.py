import logging
from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup switch platform via ExtaasDevicesManager."""
    # Haalame seadmete manageri entry-st
    manager = hass.data["extaas_template"][entry.entry_id]["devices"]

    # Lisame kõik switchid (dünaamilised switchid)
    await manager.async_add_entities(async_add_entities, entity_type="switch")