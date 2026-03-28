from aiohttp import web
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_NEW_DATA, make_device_id, make_entity_id
from .store import get_store

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView(hass))


class ExtaasApiView(web.View):

    def __init__(self, hass):
        self.hass = hass

    async def post(self):
        """Node saadab dünaamilised entity-d."""

        data = await self.request.json()
        host = data["host"]
        port = data["port"]
        entry_id = None

        # --- FIND ENTRY BY HOST ---
        for eid, e in self.hass.data[DOMAIN].items():
            if e.get("coordinator") and e["coordinator"].host == host:
                entry_id = eid
                break

        if entry_id is None:
            return web.json_response({"error": "entry not found"}, status=404)

        entry = self.hass.data[DOMAIN][entry_id]
        device_id = make_device_id(host, port)

        # --- CREATE DEVICE IF MISSING ---
        device = entry["devices"].setdefault(device_id, {
            "host": host,
            "port": port,
            "entities": {}
        })

        existing = device["entities"]
        incoming = {}

        # --- CREATE / UPDATE ENTITIES ---
        for e in data.get("node_data", []):
            uid = make_entity_id(entry_id, device_id, e["name"])
            incoming[uid] = {
                "unique_id": uid,
                "name": e["name"],
                "value": e.get("value"),
                "type": e.get("type", "sensor"),
                "icon": e.get("icon"),
            }

        # --- DELETE REMOVED ENTITIES ---
        for uid in list(existing):
            if uid not in incoming:
                existing.pop(uid)

        # --- UPSERT ---
        existing.update(incoming)

        # --- SAVE TO STORE ---
        store = get_store(self.hass)
        await store.async_save(self.hass.data[DOMAIN])

        # --- NOTIFY DYNAMIC ENTITY HANDLER ---
        async_dispatcher_send(self.hass, SIGNAL_NEW_DATA)

        return web.json_response({"ok": True})