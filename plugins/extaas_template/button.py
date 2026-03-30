from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .entities import ExtaasButton
from .const import DOMAIN, SIGNAL_UPDATE

async def async_setup_entry(hass, entry, async_add_entities):
    entities = {}

    def sync_entities(entry_id, changed):
        if entry_id != entry.entry_id:
            return

        storage = hass.data[DOMAIN].get("storage", {})
        entry_data = storage.get(entry.entry_id, {})
        data = entry_data.get("entities", {})

        new = []

        for k, v in data.items():
            # Filter type vastavalt platvormile
            if v.get("type") != "button":  # switch või button
                continue

            if k not in entities:
                ent = ExtaasButton(hass, entry, k)  # switch/button
                entities[k] = ent
                new.append(ent)
            else:
                entities[k].async_write_ha_state()

        if new:
            async_add_entities(new)

        # REMOVE entities which no longer exist
        for k in list(entities):
            if k not in data:
                ent = entities.pop(k)
                if hasattr(ent, "async_remove"):
                    hass.async_create_task(ent.async_remove())

    sync_entities(entry.entry_id, set())
    async_dispatcher_connect(hass, SIGNAL_UPDATE, sync_entities)