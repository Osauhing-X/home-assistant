# switch.py
from homeassistant.helpers.entity_platform import async_setup_platform

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return
    devices_manager = hass.data["extaas_template"][discovery_info["entry_id"]]["devices"]
    await devices_manager.async_add_entities(async_add_entities, entity_type="switch")