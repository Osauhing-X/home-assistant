from .const import DOMAIN

def get_store(hass):
    """Store all entries, devices, entities"""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "entries": {},       # { entry_id: { name, devices: { device_id: { name, host, port, icon, entities } } } }
            "entities": {},      # { entity_unique_id: entity_instance }
        }
    return hass.data[DOMAIN]