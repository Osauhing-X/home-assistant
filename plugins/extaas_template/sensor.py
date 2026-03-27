from .const import DOMAIN

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return
    devices_manager = hass.data[DOMAIN][discovery_info["entry_id"]]["devices"]
    devices_manager.setup_entities(async_add_entities, entity_type="sensor")