from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_NEW_DATA
from .entities import create_entity

class ExtaasDevicesManager:

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.entities = {}  # {unique_id: entity_instance}

    async def restore_entities(self):
        """Restore previously saved dynamic entities on startup."""
        data = self.hass.data[DOMAIN].get(self.entry.entry_id, {}).get("entities", {})
        for key, e in data.items():
            ent = create_entity(self.hass, self.entry, e)
            self.entities[e["unique_id"]] = ent

    async def async_add_entities(self, async_add_entities, entity_type):
        """Subscribe to dispatcher and add new entities on-the-fly."""
        async def handle_update(entry_id, new_data):
            if entry_id != self.entry.entry_id:
                return

            new_entities = []
            for key, e in new_data.items():
                if e["type"] != entity_type:
                    continue
                if e["unique_id"] not in self.entities:
                    ent = create_entity(self.hass, self.entry, e)
                    self.entities[e["unique_id"]] = ent
                    new_entities.append(ent)

            if new_entities:
                async_add_entities(new_entities)

        async_dispatcher_connect(self.hass, SIGNAL_NEW_DATA, handle_update)