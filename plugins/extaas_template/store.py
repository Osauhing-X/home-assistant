from .const import DOMAIN

def get_store(hass):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "connected": {},
            "value": {},
            "status": {},
            "last_seen": {},
        }
    return hass.data[DOMAIN]