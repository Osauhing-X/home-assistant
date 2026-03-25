import logging
import time

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

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

        # uus node
        if node not in store["connected"]:
            store["connected"][node] = False
            store["value"][node] = None
            store["status"][node] = "offline"

            # trigger sensor creation
            await store["add_sensor"](node)

        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

        return self.json({"status": "ok"})


async def async_setup(hass: HomeAssistant, config: dict):
    # Store
    hass.data[DOMAIN] = {
        "connected": {},
        "value": {},
        "status": {},
        "last_seen": {},
        "sensors": {},
        "add_sensor": None
    }

    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True