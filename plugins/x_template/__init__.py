import logging
import time

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, TIMEOUT, CHECK_INTERVAL

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
            store["last_seen"][node] = 0

            await store["add_sensor"](node)

        # update
        store["connected"][node] = True
        store["value"][node] = data.get("value")
        store["status"][node] = data.get("status", "online")
        store["last_seen"][node] = time.time()

        # 🔥 trigger UI update
        sensor = store["sensors"].get(node)
        if sensor:
            sensor.async_write_ha_state()

        return self.json({"status": "ok"})


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

    # 🔥 OFFLINE WATCHDOG
    async def check_nodes(now):
        store = hass.data[DOMAIN]

        for node in list(store["connected"].keys()):
            last = store["last_seen"].get(node, 0)

            if time.time() - last > TIMEOUT:
                if store["connected"].get(node):
                    store["connected"][node] = False
                    store["status"][node] = "offline"

                    sensor = store["sensors"].get(node)
                    if sensor:
                        sensor.async_write_ha_state()

    async_track_time_interval(
        hass,
        check_nodes,
        timedelta(seconds=CHECK_INTERVAL)
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True