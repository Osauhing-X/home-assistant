import time
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN
from .store import get_store

class ExtaasAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        node = data.get("node", "heartbeat")

        store = get_store(hass)

        # Update heartbeat + values
        store["connected"][node] = True
        store["value"][node] = data
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

        # Auto-discovery: kui node pole veel config entry's, lisa discovered
        if node not in store["discovered"]:
            store["discovered"][node] = {
                "name": data.get("name", f"Extaas {node}"),
                "host": data.get("host"),
                "port": data.get("port", 3000),
                "node": node,
            }

        return self.json({"ok": True})