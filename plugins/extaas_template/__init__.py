import logging
import time

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN
from .sensor import XTemplateNodeSensor

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    # Shared store
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
            node = data.get("node", "default_node")

            store = hass.data[DOMAIN]

            # Kui node pole olemas, loo sensor
            if node not in store["connected"]:
                store["connected"][node] = False
                store["value"][node] = None
                store["status"][node] = "offline"
                await store["add_sensor"](node)

            # Uuenda store
            store["connected"][node] = True
            store["value"][node] = data.get("value")
            store["status"][node] = data.get("status", "online")
            store["last_seen"][node] = time.time()

            return self.json({"status": "ok"})

    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    store = hass.data[DOMAIN]

    # Salvesta config
    store["config"] = {
        "name": entry.data.get("name"),
        "host": entry.data.get("host"),
        "port": entry.data.get("port", 3000)
    }

    # Loo Heartbeat sensor kohe
    async def add_sensor(node):
        if node in store["sensors"]:
            return
        device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": store["config"]["name"],
            "manufacturer": "Extaas",
            "model": "Node Client",
            "sw_version": f"Port {store['config']['port']}"
        }
        sensor = XTemplateNodeSensor(hass, node, device_info)
        store["sensors"][node] = sensor
        hass.async_create_task(entry.async_add_entities([sensor]))

    store["add_sensor"] = add_sensor

    # Loo kohe Heartbeat sensori (default node)
    await add_sensor("heartbeat")

    # Forward setup sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True