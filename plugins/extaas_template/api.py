from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_NEW_DATA

class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        entry_id = data["node_name"]
        node_data = data.get("node_data", [])

        if DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]["coordinator"]

            # Muudame node_full ja node_data
            coordinator.node_full = {
                d["name"]: d for d in node_data
            }
            # dispatcher, et sensorid ja switchid uuenduksid / loodusid
            async_dispatcher_send(hass, SIGNAL_NEW_DATA, entry_id)

        return self.json({"ok": True})

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)