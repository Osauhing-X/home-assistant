import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, DATA
from .helper import get_device_info, update_last_seen
from .sensor import XTemplateNodeSensor

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
    """Basic setup, HTTP API register."""
    hass.data[DOMAIN] = DATA.copy()
    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup entry and heartbeat sensor."""
    store = hass.data[DOMAIN]
    store["config"] = entry.data

    async def add_sensor(node: str):
        """Loo sensor kui seda veel pole."""
        if node in store["sensors"]:
            return

        sensor = XTemplateNodeSensor(hass, node, get_device_info(node, entry.data))
        store["sensors"][node] = sensor

        # Sensorid lisatakse async_add_entities kaudu sensor.py-st
        # siia lihtsalt forward entry setup sensoriplatvormile
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

        return sensor

    store["add_sensor"] = add_sensor

    # Loome kohe heartbeat sensor
    await add_sensor("heartbeat")

    return True