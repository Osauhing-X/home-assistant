from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .entities import ExtaasEntity
from .const import DOMAIN, SIGNAL_UPDATE

class ExtaasSensor(ExtaasEntity):
    @property
    def state(self):
        return self.data.get("value")

async def async_setup_entry(hass, entry, async_add_entities):
    entities = {}

    def add_entities(entry_id, changed):
        if entry_id != entry.entry_id:
            return
        storage = hass.data[DOMAIN].get("storage", {})
        data = storage.get(entry.entry_id, {}).get("entities", {})
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

    add_entities(entry.entry_id, set())
    async_dispatcher_connect(hass, SIGNAL_UPDATE, add_entities)