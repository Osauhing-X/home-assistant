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

        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

        # trigger update
        hass.states.async_set(f"sensor.x_{node}", True)

        return self.json({"ok": True})