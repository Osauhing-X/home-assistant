# store.py
from homeassistant.helpers.storage import Store
from .const import DOMAIN

STORE_VERSION = 1
STORE_KEY = DOMAIN  # 👉 üks tõeallikas

def get_store(hass):
    return Store(hass, STORE_VERSION, STORE_KEY)