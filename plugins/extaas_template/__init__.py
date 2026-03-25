import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {
        "connected": {},
        "value": {},
        "status": {},
        "last_seen": {},
        "sensors": {},
        "config": {},
        "add_sensor": None
    }

    # HTTP API
    class XTemplateAPI(HomeAssistantView):
        url = "/api/extaas_template"
        name = "api:extaas_template"
        requires_auth = False

        async def post(self, request):
            hass: HomeAssistant = request.app["hass"]
            data = await request.json()
            node = data.get("node", "heartbeat")

            store = hass.data[DOMAIN]

            if node not in store["connected"]:
                store["connected"][node] = False
                store["value"][node] = None
                store["status"][node] = "offline"

                # lisame sensori
                if store["add_sensor"]:
                    await store["add_sensor"](node)

            store["connected"][node] = True
            store["value"][node] = data.get("value")
            store["status"][node] = data.get("status", "online")
            import time
            store["last_seen"][node] = time.time()

            return self.json({"status": "ok"})

    hass.http.register_view(XTemplateAPI)
    return True

async def async_setup_entry(hass, entry: ConfigEntry):
    store = hass.data[DOMAIN]

    # Salvesta config
    store["config"] = {
        "name": entry.data.get("name"),
        "host": entry.data.get("host"),
        "port": entry.data.get("port", 3000)
    }

    # Forward sensor platvormi setup
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True