import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .helpers import make_device_info, update_node_status

_LOGGER = logging.getLogger(__name__)

class XTemplateAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass: HomeAssistant = request.app["hass"]
        data = await request.json()
        node = data.get("node", "unknown")

        store = hass.data[DOMAIN]

        # uus node sensorite jaoks
        if node not in store["sensors"]:
            device_info = make_device_info(node, store["config"].get("host"), store["config"].get("port"))
            await store["add_sensor"](node, device_info)

        update_node_status(store, node, data.get("value"), data.get("status", "online"))

        return self.json({"status": "ok"})


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {
        "connected": {},
        "value": {},
        "status": {},
        "last_seen": {},
        "sensors": {},
        "add_sensor": None,
        "config": {}
    }

    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    store = hass.data[DOMAIN]
    store["config"] = entry.data  # salvesta host/port/nimi config

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True