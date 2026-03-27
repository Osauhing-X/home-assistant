import logging
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform via ExtaasDevicesManager."""
    # Haalame seadmete manageri entry-st
    manager = hass.data["extaas_template"][entry.entry_id]["devices"]

    # Lisame kõik sensorid (sh Heartbeat + dünaamilised sensorid)
    await manager.async_add_entities(async_add_entities, entity_type="sensor")