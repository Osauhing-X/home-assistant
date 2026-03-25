from .const import DOMAIN

def get_store(hass):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "connected": {},  # node -> True/False
            "value": {},      # node -> dynamic key-values
            "status": {},     # node -> status string
            "last_seen": {},  # node -> timestamp
            "entities": {}    # node -> HA entity objects
        }
    return hass.data[DOMAIN]