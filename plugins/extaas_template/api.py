# api.pySSS
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
            devices_manager = hass.data[DOMAIN][entry_id]["devices"]

            # Update coordinator
            coordinator.dynamic_entities = node_data

            # Uuenda/loo devices ja entity-d
            devices_manager.update_node_data(node_data)

            # Teavitame HA-sse, et state uuenduks
            async_dispatcher_send(hass, SIGNAL_NEW_DATA, entry_id)

        return self.json({"ok": True})

async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)