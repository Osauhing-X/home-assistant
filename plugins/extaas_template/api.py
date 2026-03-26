from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN


class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        # ✅ UUS STRUKTUUR
        node_name = data.get("node_name")
        host = data.get("host")
        port = data.get("port")
        service_name = data.get("service_name")
        node_data = data.get("nodeData", [])

        if not node_name or not service_name:
            return self.json({"error": "invalid payload"}, status_code=400)

        payload = {
            "node_name": node_name,
            "host": host,
            "port": port,
            "service_name": service_name,
            "nodeData": node_data
        }

        # ✅ oluline: await
        if "update_entities" in hass.data[DOMAIN]:
            await hass.data[DOMAIN]["update_entities"](payload)

        return self.json({"ok": True})


async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)