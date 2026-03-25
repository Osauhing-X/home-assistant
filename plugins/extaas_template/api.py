import time
from homeassistant.components.http import HomeAssistantView
from .store import get_store
from .const import DOMAIN

class ExtaasAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        node = data.get("node", "heartbeat")
        store = get_store(hass)

        # Uuendame heartbeat ja dynamic keys
        store["connected"][node] = True
        store["last_seen"][node] = time.time()
        store["status"][node] = data.get("status", "online")
        store["value"][node] = {k: v for k, v in data.items() if k not in ["node", "integration"]}

        return self.json({"ok": True})