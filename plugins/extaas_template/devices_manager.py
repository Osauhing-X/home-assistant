# devices_manager.py
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
        data = self.hass.data[DOMAIN][self.entry.entry_id]

        for device in data["devices"].values():
            for e in device["entities"].values():
                entity = create_entity(self.hass, self.entry, device, e)
                self.entities[e["unique_id"]] = entity

    async def async_add_entities(self, async_add_entities, entity_type):
        """Subscribe to dispatcher and add new entities on-the-fly."""

        async def handle_update():
            data = self.hass.data[DOMAIN][self.entry.entry_id]
            new = []

            for device in data["devices"].values():
                for e in device["entities"].values():

                    if e["type"] != entity_type:
                        continue

                    if e["unique_id"] not in self.entities:
                        ent = create_entity(self.hass, self.entry, device, e)
                        self.entities[e["unique_id"]] = ent
                        new.append(ent)

            if new:
                async_add_entities(new)

        async_dispatcher_connect(self.hass, SIGNAL_NEW_DATA, handle_update)
        await handle_update()