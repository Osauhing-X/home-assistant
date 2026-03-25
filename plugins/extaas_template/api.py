from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN
from .helper import normalize_value

class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        node = data.get("node")
        if not node:
            return self.json({"error": "missing node"}, status_code=400)

        store = hass.data[DOMAIN]["store"]
        clean = {
            k: normalize_value(v)
            for k, v in data.items()
            if k not in ["node", "integration"]
        }
        store.update_node(node, clean)

        if "update_entities" in hass.data[DOMAIN]:
            hass.data[DOMAIN]["update_entities"](node)

        return self.json({"ok": True})

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)