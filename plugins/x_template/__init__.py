import logging
import time

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class API(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass: HomeAssistant = request.app["hass"]
        data = await request.json()

        node = data.get("node")
        store = hass.data[DOMAIN]

        entry_id = store["nodes"].get(node)

        if not entry_id:
            return self.json({"error": "unknown node"}, status=404)

        sensor = store["entities"][entry_id]

        sensor._connected = True
        sensor._value = data.get("value")
        sensor._last_seen = time.time()

        sensor.async_write_ha_state()

        return self.json({"status": "ok"})


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {
        "entities": {},
        "nodes": {}
    }

    hass.http.register_view(API)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    hass.data[DOMAIN]["entities"].pop(entry.entry_id, None)
    hass.data[DOMAIN]["nodes"].pop(entry.data["name"], None)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)