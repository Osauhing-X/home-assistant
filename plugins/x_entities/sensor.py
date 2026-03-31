# sensor.py
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .entities import ExtaasSensor
from .const import DOMAIN, SIGNAL_ENTITY


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]

    # -------------------------
    # INITIAL LOAD
    # -------------------------
    entities = [
        ExtaasSensor(hass, entry, k)
        for k, v in data.items()
        if v.get("type") == "sensor"
    ]

    async_add_entities(entities)

    # -------------------------
    # DYNAMIC ADD
    # -------------------------
    async def handle_new(eid, keys):
        if eid != entry.entry_id:
            return

        new = []
        current = hass.data[DOMAIN][entry.entry_id]["entities"]

        for k in keys:
            v = current.get(k)
            if not v or v.get("type") != "sensor":
                continue

            new.append(ExtaasSensor(hass, entry, k))

        if new:
            async_add_entities(new)

    async_dispatcher_connect(hass, SIGNAL_ENTITY, handle_new)