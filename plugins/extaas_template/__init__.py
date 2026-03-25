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

            device_info = {
                "identifiers": {(DOMAIN, node)},
                "name": node,
                "manufacturer": "Extaas",
                "model": "Node Client",
                "sw_version": f"Port {store['config'].get('port', 3000)}",
                "entry_type": "service",
            }

            # trigger sensor creation
            await store["add_sensor"](node, device_info)

        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

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
    store["config"] = entry.data

    # Dummy heartbeat sensor, et integratsioon ilmuks kohe Devices & Services lehel
    dummy_node = f"{entry.entry_id}_heartbeat"
    if dummy_node not in store["sensors"]:
        from .sensor import XTemplateNodeSensor
        device_info = {
            "identifiers": {(DOMAIN, dummy_node)},
            "name": entry.data.get("name", "X Template"),
            "manufacturer": "Extaas",
            "model": "Node Client",
            "sw_version": f"Port {entry.data.get('port', 3000)}",
            "entry_type": "service",
        }
        sensor = XTemplateNodeSensor(hass, dummy_node, device_info)
        store["sensors"][dummy_node] = sensor
        sensor.async_write_ha_state()

    # Funktsioon Node sensorite lisamiseks
    async def add_sensor(node, device_info):
        if node in store["sensors"]:
            return
        from .sensor import XTemplateNodeSensor
        sensor = XTemplateNodeSensor(hass, node, device_info)
        store["sensors"][node] = sensor
        sensor.async_write_ha_state()

    store["add_sensor"] = add_sensor

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True