from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN

class ExtaasAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        node_name = data.get("node_name")
        host = data.get("host")
        port = data.get("port")

        for coordinator in hass.data.get(DOMAIN, {}).values():
            if (
                coordinator.host == host and
                coordinator.port == port and
                coordinator.name == data.get("service_name")
            ):
                coordinator.update_from_api(data)

        return self.json({"ok": True})


async def async_setup_api(hass):
    hass.http.register_view(ExtaasAPI)