from .const import DOMAIN

def get_store(hass):
    """Tagasta store dict."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {
            "connected": {},
            "last_seen": {},
            "entities": {},       # node -> key -> value
            "discovered": {},     # node -> {name, info...}
        }
    return hass.data[DOMAIN]