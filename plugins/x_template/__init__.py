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

        node = data.get("node")
        store = hass.data[DOMAIN]

        sensor = store["entities"].get(node)

        if not sensor:
            return self.json({"error": "unknown node"}, status=404)

        sensor._connected = True
        sensor._value = data.get("value")
        sensor._status = data.get("status", "online")
        sensor._last_seen = time.time()

        sensor.async_write_ha_state()

        return self.json({"status": "ok"})


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["entities"] = {}

    hass.http.register_view(XTemplateAPI)

    async def watchdog(now):
        for sensor in hass.data[DOMAIN]["entities"].values():
            if time.time() - sensor._last_seen > TIMEOUT:
                if sensor._connected:
                    sensor._connected = False
                    sensor._status = "offline"
                    sensor.async_write_ha_state()

    async_track_time_interval(hass, watchdog, timedelta(seconds=CHECK_INTERVAL))

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    try:
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        return True
    except Exception as e:
        _LOGGER.error("Setup failed: %s", e)
        return False


# 🔥 SEE ON KRIITILINE
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN]["entities"].pop(entry.data["name"], None)

    return unload_ok