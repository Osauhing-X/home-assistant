import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from .sensor import XTemplateNodeSensor, async_add_sensor

_LOGGER = logging.getLogger(__name__)
DOMAIN = "x_template"

# Shared runtime state
DATA = {
    "connected": {},  # node_name -> True/False
    "value": {},      # node_name -> viimati saadud value
    "status": {}      # node_name -> string status
}

class XTemplateAPI(HomeAssistantView):
    url = "/api/x_template"
    name = "api:x_template"
    requires_auth = False  # ainult dev, hiljem True

    async def post(self, request):
        """Node rakendus POSTib oma staatuse"""
        hass: HomeAssistant = request.app["hass"]
        data = await request.json()
        node_name = data.get("node", "unknown")

        # Kui uus Node, lisame runtime-s
        if node_name not in DATA["connected"]:
            DATA["connected"][node_name] = False
            DATA["value"][node_name] = None
            DATA["status"][node_name] = "offline"
            # Trigger sensorite loomist HA-s
            await async_add_sensor(hass, node_name)

        # Update väärtused
        DATA["connected"][node_name] = True
        DATA["value"][node_name] = data.get("value")
        DATA["status"][node_name] = data.get("status", "online")

        # Värskenda HA state
        hass.states.async_set(
            f"{DOMAIN}.{node_name}",
            str(DATA["value"][node_name]),
            {"connected": DATA["connected"][node_name], "status": DATA["status"][node_name]}
        )

        return self.json({"status": "ok"})

    async def get(self, request):
        return self.json(DATA)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.http.register_view(XTemplateAPI)
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    # Kui peaksid hiljem lisama config entries, sensorid seadistatakse siit
    return True