from .const import DOMAIN

def get_store(hass):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "connected": {},
            "entities": {},
            "last_seen": {}
        }
    return hass.data[DOMAIN]