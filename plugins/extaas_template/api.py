from homeassistant.components.http import HomeAssistantView
from .store import get_store

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

        if node not in store["entities"]:
            store["entities"][node] = {}

        # Dünaamilised võtmed
        keys_to_remove = set(store["entities"][node].keys()) - set(data.keys())
        for key in keys_to_remove:
            del store["entities"][node][key]

        for key, value in data.items():
            if key in ["node", "integration"]:
                continue
            store["entities"][node][key] = value

        store["connected"][node] = True
        store["last_seen"][node] = data.get("timestamp")

        # Trigger heartbeat update
        hass.states.async_set(f"sensor.x_{node}_heartbeat", store["connected"].get(node, False))

        return self.json({"ok": True})