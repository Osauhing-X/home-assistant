from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN

class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        if "update_entities" in hass.data[DOMAIN]:
            await hass.data[DOMAIN]["update_entities"](data)

        return self.json({"ok": True})

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)