# api.py
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
    requires_auth = False  # 🔥 lubab ilma authita

    def __init__(self, hass):
        self.hass = hass
        self._save_task = None

    async def post(self, request):
        try:
            data = await request.json()
        except Exception as err:
            _LOGGER.warning("Invalid JSON received: %s", err)
            return web.json_response({"error": "invalid JSON"}, status=400)

        host = data.get("host")
        port = data.get("port")

        if not host or not port:
            return web.json_response({"error": "host or port missing"}, status=400)

        entry_id = None
        entry_obj = None

        # Otsi entry
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry is None or entry.data is None:
                continue
            if entry.data.get("host") == host and entry.data.get("port") == port:
                entry_id = entry.entry_id
                entry_obj = entry
                break

        if not entry_id or entry_id not in self.hass.data.get(DOMAIN, {}):
            _LOGGER.warning(
                "No configured entry found for host %s:%s. Ignoring POST.", host, port
            )
            return web.json_response({"error": "entry not found"}, status=404)

        entry_data = self.hass.data[DOMAIN][entry_id]
        existing = entry_data.get("entities", {})
        incoming = data.get("node_data", {})

        if len(incoming) > MAX_ENTITIES_PER_NODE:
            return web.json_response({"error": "too many entities"}, status=400)

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

        return web.json_response({"ok": True})

    def _debounce_save(self):
        """Salvesta 2 sekundi pärast, ühteaegu ainult üks salvestus"""
        if self._save_task:
            self._save_task.cancel()

        async def save():
            await asyncio.sleep(2)
            store = get_store(self.hass)

            # 👉 ainult serialiseeritav data
            clean_data = {}

            for entry_id, entry_data in self.hass.data[DOMAIN].items():
                if entry_id == "session":
                    continue
                
                clean_data[entry_id] = {
                    "entities": entry_data.get("entities", {}) }

            await store.async_save(clean_data)


async def async_setup_api(hass):
    """Register API endpoint"""
    hass.http.register_view(ExtaasApiView(hass))