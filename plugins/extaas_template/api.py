import asyncio
import logging
from aiohttp import web

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, SIGNAL_UPDATE, MAX_ENTITIES_PER_NODE, SIGNAL_ENTITY
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
        # -------------------------
        # SAFE JSON
        # -------------------------
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid JSON"}, status=400)

        host = data.get("host")
        port = data.get("port")

        if not host or not port:
            return web.json_response({"error": "host or port missing"}, status=400)

        # -------------------------
        # FIND ENTRY
        # -------------------------
        entry_id = None

        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.data.get("host") == host and entry.data.get("port") == port:
                entry_id = entry.entry_id
                break

        if not entry_id or entry_id not in self.hass.data[DOMAIN]:
            return web.json_response({"error": "entry not found"}, status=404)

        entry_data = self.hass.data[DOMAIN][entry_id]

        existing = entry_data.get("entities", {})
        incoming = data.get("node_data", {})

        if len(incoming) > MAX_ENTITIES_PER_NODE:
            return web.json_response({"error": "too many entities"}, status=400)

        changed = set()
        new_entities = []

        # -------------------------
        # DELETE
        # -------------------------
        for k in list(existing):
            if k not in incoming:
                existing.pop(k)
                changed.add(k)

        # -------------------------
        # UPSERT
        # -------------------------
        for k, v in incoming.items():
            is_new = k not in existing

            if is_new or existing[k].get("value") != v.get("value"):
                changed.add(k)

            existing[k] = {
                "value": v.get("value"),
                "type": v.get("type", "sensor"),
                "icon": v.get("icon"),
                "name": v.get("name", k),  # ✅ FIX
            }

            if is_new:
                new_entities.append(k)

        # -------------------------
        # SAVE (debounced, SAFE)
        # -------------------------
        self._debounce_save()

        # 👉 update existing entities
        async_dispatcher_send(self.hass, SIGNAL_UPDATE, entry_id, changed)

        # 👉 create new entities instantly
        if new_entities:
            async_dispatcher_send(self.hass, SIGNAL_ENTITY, entry_id, new_entities)

        return web.json_response({"ok": True})

    def _debounce_save(self):
        if self._save_task:
            self._save_task.cancel()

        async def save():
            await asyncio.sleep(2)

            store = get_store(self.hass)

            # 👉 ONLY SERIALIZABLE DATA
            clean = {}

            for key, value in self.hass.data[DOMAIN].items():
                if key == "_runtime":
                    continue

                clean[key] = {
                    "entities": value.get("entities", {})
                }

            await store.async_save(clean)

        self._save_task = self.hass.loop.create_task(save())


async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView(hass))