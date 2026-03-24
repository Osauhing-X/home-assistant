import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from .const import DATA, DOMAIN
from .sensor import async_add_sensor

_LOGGER = logging.getLogger(__name__)

class XTemplateAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass: HomeAssistant = request.app["hass"]
        data = await request.json()
        node_name = data.get("node", "unknown")

        if node_name not in DATA["connected"]:
            DATA["connected"][node_name] = False
            DATA["value"][node_name] = None
            DATA["status"][node_name] = "offline"

            await async_add_sensor(hass, node_name)

        DATA["connected"][node_name] = True
        DATA["value"][node_name] = data.get("value")
        DATA["status"][node_name] = data.get("status", "online")

        hass.states.async_set(
            f"{DOMAIN}.{node_name}",
            str(DATA["value"][node_name]),
            {
                "connected": DATA["connected"][node_name],
                "status": DATA["status"][node_name]
            }
        )

        return self.json({"status": "ok"})


async def async_setup(hass: HomeAssistant, config: dict):
    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    return True