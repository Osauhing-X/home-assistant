from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_ENTITY
from .entities import ExtaasBinarySensor


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    async_add_entities([
        ExtaasBinarySensor(hass, entry, key)
        for key, value in data.items()
        if value.get("type") == "binary_sensor"
    ])

    @callback
    def handle_new(entry_id, keys):
        if entry_id != entry.entry_id:
            return
        current = hass.data[DOMAIN][entry.entry_id]["entities"]
        entities = [
            ExtaasBinarySensor(hass, entry, key)
            for key in keys
            if current.get(key, {}).get("type") == "binary_sensor"
        ]
        if entities:
            async_add_entities(entities)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ENTITY, handle_new)
    )
