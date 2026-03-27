from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    """Dummy sensor platvorm – registreerib callback devices_manageris."""
    devices_manager = hass.data[DOMAIN][entry.entry_id]["devices"]
    devices_manager.register_platform("sensor", async_add_entities)
    return True