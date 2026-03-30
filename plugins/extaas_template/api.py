import asyncio
import logging
from aiohttp import web
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN, SIGNAL_UPDATE, MAX_ENTITIES_PER_NODE
from .store import get_store

_LOGGER = logging.getLogger(__name__)


class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    def __init__(self, hass):
        self.hass = hass
        self._save_task = None

    async def post(self, request):
        data = await request.json()

        host = data.get("host")
        port = data.get("port")

        if not host or not port:
            return web.json_response({"error": "host or port missing"}, status=400)

        entry_id = None
        entry_obj = None

        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if not entry or not entry.data:
                continue

            if entry.data.get("host") == host and entry.data.get("port") == port:
                entry_id = entry.entry_id
                entry_obj = entry
                break

        if not entry_id or entry_id not in self.hass.data.get(DOMAIN, {}):
            _LOGGER.warning("Unknown node %s:%s", host, port)
            return web.json_response({"error": "entry not found"}, status=404)

        entry_data = self.hass.data[DOMAIN][entry_id]
        existing = entry_data.setdefault("entities", {})
        incoming = data.get("node_data", {})

        if len(incoming) > MAX_ENTITIES_PER_NODE:
            return web.json_response({"error": "too many entities"}, status=400)

        changed = set()

        # DELETE
        for k in list(existing):
            if k not in incoming:
                existing.pop(k)
                changed.add(k)

        # UPSERT
        for k, v in incoming.items():
            prev = existing.get(k, {})

            if prev.get("value") != v.get("value"):
                changed.add(k)

            existing[k] = {
                "value": v.get("value"),
                "type": v.get("type", "sensor"),
                "icon": v.get("icon"),
                "name": v.get("name", k),
                "device": v.get("device", "default"),
            }

        self._debounce_save()

        async_dispatcher_send(self.hass, SIGNAL_UPDATE, entry_id, changed)

        return web.json_response({"ok": True})

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