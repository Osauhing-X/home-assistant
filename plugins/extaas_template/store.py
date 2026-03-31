from .const import DOMAIN, SIGNAL_NEW_DATA
from homeassistant.helpers.dispatcher import async_dispatcher_send

def update_entity(hass, entry_id, key, value, type_="sensor", icon=None):
    """Lisa või uuenda entity state ja saadab signal uute entityde kohta."""
    entry_data = hass.data.setdefault(DOMAIN, {}).setdefault(entry_id, {})
    entities = entry_data.setdefault("entities", {})

    if key not in entities:
        entities[key] = {"unique_id": key, "name": key, "type": type_, "value": value, "icon": icon}
    else:
        entities[key]["value"] = value
        if icon:
            entities[key]["icon"] = icon

    async_dispatcher_send(hass, SIGNAL_NEW_DATA, entry_id, {key: entities[key]})