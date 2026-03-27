from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_NEW_DATA
from .registry import async_cleanup_entities


class ExtaasApiView(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        entry_id = data["node_name"]
        node_list = data.get("node_data", [])

        if DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            store = hass.data[DOMAIN][entry_id]

            # full data
            full_data = {
                d["name"]: {
                    "value": d.get("value"),
                    "type": d.get("type", "sensor"),
                    "icon": d.get("icon"),
                }
                for d in node_list
            }

            store["node_full"] = full_data

            # values only
            node_values = {k: v["value"] for k, v in full_data.items()}

            coordinator = store["coordinator"]
            coordinator.node_data = node_values
            coordinator.async_set_updated_data(node_values)

            # 🔥 entity removal
            valid_ids = {
                f"{coordinator.host}:{coordinator.port}_{k}"
                for k in full_data.keys()
            }

            await async_cleanup_entities(hass, coordinator.entry, valid_ids)

            # 🔥 dynamic add trigger
            async_dispatcher_send(hass, SIGNAL_NEW_DATA, entry_id)

        return self.json({"ok": True})


async def async_setup_api(hass):
    hass.http.register_view(ExtaasApiView)