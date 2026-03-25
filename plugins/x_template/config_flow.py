import logging
import time

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ExtaasAPI(HomeAssistantView):
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass: HomeAssistant = request.app["hass"]
        data = await request.json()

        node = data.get("node")
        store = hass.data[DOMAIN]

        for sensor in store["entities"].values():
            if sensor.node_name == node:
                sensor.connected = True
                sensor.value = data.get("value")
                sensor.status = data.get("status", "online")
                sensor.last_seen = time.time()
                sensor.async_write_ha_state()
                return self.json({"status": "ok"})

        return self.json({"error": "node not found"}, status=404)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["entities"] = {}

    hass.http.register_view(ExtaasAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN]["entities"].pop(entry.entry_id, None)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)