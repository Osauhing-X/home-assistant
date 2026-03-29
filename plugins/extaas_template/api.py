from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_UPDATE, MAX_ENTITIES_PER_NODE
from .store import get_store
import asyncio

class ExtaasApiView(HomeAssistantView):
    """API endpoint for Extaas."""

    url = "/api/extaas_template"  # <--- siin määrad oma endpointi
    name = "api:extaas_template"  # unikaalne nimi Home Assistantile

    def __init__(self, hass):
        self.hass = hass
        self._save_task = None

    async def post(self, request):
        data = await request.json()

        host = data["host"]
        port = data["port"]

        entry_id = None
        for eid in self.hass.data[DOMAIN]:
            entry = self.hass.config_entries.async_get_entry(eid)
            if entry.data["host"] == host and entry.data["port"] == port:
                entry_id = eid
                break

        if not entry_id:
            return self.json({"error": "entry not found"}, status=404)

        entry = self.hass.data[DOMAIN][entry_id]
        existing = entry["entities"]
        incoming = data.get("node_data", {})

        if len(incoming) > MAX_ENTITIES_PER_NODE:
            return self.json({"error": "too many entities"}, status=400)

        changed = set()

        # delete
        for k in list(existing):
            if k not in incoming:
                existing.pop(k)
                changed.add(k)

        # upsert
        for k, v in incoming.items():
            if k not in existing or existing[k].get("value") != v.get("value"):
                changed.add(k)

            existing[k] = {
                "value": v.get("value"),
                "type": v.get("type", "sensor"),
                "icon": v.get("icon")
            }

        self._debounce_save()

        async_dispatcher_send(self.hass, SIGNAL_UPDATE, entry_id, changed)

        return self.json({"ok": True})

    def _debounce_save(self):
        if self._save_task:
            self._save_task.cancel()

        async def save():
            await asyncio.sleep(2)
            store = get_store(self.hass)
            await store.async_save(self.hass.data[DOMAIN])

        self._save_task = self.hass.loop.create_task(save())


async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView(hass))