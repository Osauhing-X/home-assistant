from homeassistant.helpers.storage import Store

STORE_KEY = "extaas_template_store"
STORE_VERSION = 1

def get_store(hass):
    return Store(hass, STORE_VERSION, STORE_KEY)