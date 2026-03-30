from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .entities import ExtaasSensor
from .const import DOMAIN, SIGNAL_UPDATE

async def async_setup_entry(hass, entry, async_add_entities):
    entities = {}

    def add_missing_entities(entry_id, changed):
        if entry_id != entry.entry_id:
            return

        storage = hass.data[DOMAIN].get("storage", {})
        entry_data = storage.get(entry.entry_id, {})
        data = entry_data.get("entities", {})

        new = []
        for k, v in data.items():
            if v.get("type") != "sensor":
                continue
            if k not in entities:
                ent = ExtaasSensor(hass, entry, k)
                entities[k] = ent
                new.append(ent)

        if new:
            async_add_entities(new)

    # initial load
    add_missing_entities(entry.entry_id, set())

    # listen for updates
    async_dispatcher_connect(hass, SIGNAL_UPDATE, add_missing_entities)