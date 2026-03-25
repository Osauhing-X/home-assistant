import time
from homeassistant.components.http import HomeAssistantView
from .store import get_store
from .helper import update_last_seen

class ExtaasAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        node = data.get("node")
        if not node:
            return self.json({"ok": False, "error": "Missing node"})

        store = get_store(hass)
        store["connected"][node] = True
        store["last_seen"][node] = time.time()
        store.setdefault("entities", {}).setdefault(node, {})

        # Dünaamilised keyd
        for key, value in data.items():
            if key != "node":
                store["entities"][node][key] = value

        # Heartbeat trigger
        hass.states.async_set(f"sensor.x_{node}_heartbeat", store["connected"].get(node, False))

        # Auto-discovery
        if node not in store["discovered"]:
            store["discovered"][node] = {"name": f"Extaas {node}"}
            # Võid siin lisada notifikatsiooni Home Assistant UI-le

        return self.json({"ok": True})