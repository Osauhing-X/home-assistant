from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN

class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        # Node name -> entry_id
        entry_id = data["node_name"]
        if DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            # uuenda node_data
            hass.data[DOMAIN][entry_id]["node_data"] = {
                d["name"]: d["value"] for d in data.get("node_data", [])
            }

        return self.json({"ok": True})

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)