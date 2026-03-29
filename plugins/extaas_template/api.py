from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_UPDATE, MAX_ENTITIES_PER_NODE
from .store import get_store
import asyncio

class ExtaasApiView(HomeAssistantView):
    """API endpoint for Extaas."""

    url = "/api/extaas_template"  # määrab API tee
    name = "api:extaas_template"  # unikaalne Home Assistantis

    _save_task = None

    async def post(self, request):
        hass = request.app["hass"]  # Home Assistant instants
        data = await request.json()

        host = data["host"]
        port = data["port"]

        entry_id = None
        for eid in hass.data[DOMAIN]:
            entry = hass.config_entries.async_get_entry(eid)
            if entry.data["host"] == host and entry.data["port"] == port:
                entry_id = eid
                break

        if not entry_id:
            return self.json({"error": "entry not found"}, status=404)

        entry = hass.data[DOMAIN][entry_id]
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

        self._debounce_save(hass)

        async_dispatcher_send(hass, SIGNAL_UPDATE, entry_id, changed)

        return self.json({"ok": True})

    def _debounce_save(self, hass):
        if self._save_task:
            self._save_task.cancel()

        async def save():
            await asyncio.sleep(2)
            store = get_store(hass)
            await store.async_save(hass.data[DOMAIN])

        self._save_task = hass.loop.create_task(save())


async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)