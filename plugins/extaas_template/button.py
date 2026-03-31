from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .entities import ExtaasEntity
from .const import DOMAIN, SIGNAL_UPDATE

class ExtaasButton(ExtaasEntity):
    async def async_press(self):
        runtime = self.hass.data[DOMAIN].get("runtime", {})
        session = runtime.get("session")
        if session is None:
            return
        # simulate button press
        self.data["value"] = not self.data.get("value", False)

async def async_setup_entry(hass, entry, async_add_entities):
    entities = {}

    def add_entities(entry_id, changed):
        if entry_id != entry.entry_id:
            return
        storage = hass.data[DOMAIN].get("storage", {})
        data = storage.get(entry.entry_id, {}).get("entities", {})
        new = []
        for k, v in data.items():
            if v.get("type") != "button":
                continue
            if k not in entities:
                ent = ExtaasButton(hass, entry, k)
                entities[k] = ent
                new.append(ent)
        if new:
            async_add_entities(new)

    add_entities(entry.entry_id, set())
    async_dispatcher_connect(hass, SIGNAL_UPDATE, add_entities)