from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_NEW_DATA
from .entities import create_entity

class ExtaasDevicesManager:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.entities = {}

    async def restore_entities(self):
        data = self.hass.data[DOMAIN].setdefault(self.entry.entry_id, {"entities": {}})
        for e in data.get("entities", {}).values():
            entity = create_entity(self.hass, self.entry, e)
            self.entities[e["unique_id"]] = entity

    async def async_add_entities(self, async_add_entities, entity_type):
        async def handle_update(entry_id, changed):
            if entry_id != self.entry.entry_id:
                return
            storage = self.hass.data[DOMAIN].get(self.entry.entry_id, {})
            data = storage.get("entities", {})
            new = []
            for e in data.values():
                if e.get("type") != entity_type:
                    continue
                if e["unique_id"] not in self.entities:
                    ent = create_entity(self.hass, self.entry, e)
                    self.entities[e["unique_id"]] = ent
                    new.append(ent)
            if new:
                async_add_entities(new)
        async_dispatcher_connect(self.hass, SIGNAL_NEW_DATA, handle_update)
        await handle_update(self.entry.entry_id, set())