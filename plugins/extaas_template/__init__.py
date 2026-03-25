import logging

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, DATA
from .helper import get_device_info, update_last_seen

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

        if node not in store["connected"]:
            store["connected"][node] = False
            store["value"][node] = None
            store["status"][node] = "offline"

            # trigger sensor creation
            await store["add_sensor"](node)

        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")

        update_last_seen(hass, node)

        return self.json({"status": "ok"})

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = DATA.copy()
    hass.http.register_view(XTemplateAPI)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    store = hass.data[DOMAIN]
    store["config"] = entry.data

    from .sensor import XTemplateNodeSensor

    async def add_sensor(node):
        if node in store["sensors"]:
            return
        sensor = XTemplateNodeSensor(hass, node, get_device_info(node, entry.data))
        store["sensors"][node] = sensor
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
        entry.async_add_listener(lambda e: None)
        entry.async_create_task(sensor)  # <- heartbeat sensor loomine
        return sensor

    store["add_sensor"] = add_sensor

    # loome kohe heartbeat sensorid
    await add_sensor("heartbeat")

    return True