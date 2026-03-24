from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "x_template"

PLATFORMS = ["switch"]

# Shared state
DATA = {
    "connected": False,
    "value": None
}


class XTemplateAPI(HomeAssistantView):
    url = "/api/x_template"
    name = "api:x_template"
    requires_auth = False  # dev only!

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        _LOGGER.warning(f"Received from Node: {data}")

        DATA["connected"] = True
        DATA["value"] = data.get("value")

        # update entity
        hass.states.async_set(
            "x_template.data",
            str(DATA["value"]),
            {"connected": True}
        )

        return self.json({"status": "ok"})

    async def get(self, request):
        return self.json(DATA)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True