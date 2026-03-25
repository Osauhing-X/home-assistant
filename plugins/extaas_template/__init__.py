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

        # Kui sensor puudub, loo see
        if node not in store["sensors"]:
            await store["add_sensor"](node, self.get_device_info(node, data))

        # uuenda state
        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

        # uuenda kõik seotud sensorid HA-s
        for sensor in store["sensors"].values():
            if sensor.node == node:
                sensor.async_write_ha_state()

        return self.json({"status": "ok"})

    def get_device_info(self, node, data):
        return {
            "identifiers": {(DOMAIN, node)},
            "name": node,
            "manufacturer": "Extaas",
            "model": "Node Client",
            "sw_version": f"Port {data.get('port', 3000)}",
            "entry_type": "service",
        }

async def async_setup(hass: HomeAssistant, config: dict):
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
    store = hass.data[DOMAIN]

    # Funktsioon sensori loomiseks
    async def add_sensor(node, device_info):
        from .sensor import XTemplateNodeSensor
        sensor = XTemplateNodeSensor(hass, node, device_info)
        store["sensors"][node] = sensor
        hass.async_create_task(entry.async_forward_entry_setups(["sensor"]))
        sensor.async_write_ha_state()

    store["add_sensor"] = add_sensor
    return True