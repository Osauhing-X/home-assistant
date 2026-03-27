import time
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN
from .store import get_store
from .sensor import XSensor

class ExtaasAPI(HomeAssistantView):
    """Node -> HA push API."""

    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        node = data.get("node")
        host = data.get("host")
        port = data.get("port", 3000)

        store = get_store(hass)

        # Auto-discovery
        if node not in store["nodes"]:
            # Salvesta discovered node
            store["discovered_nodes"][node] = {
                "host": host,
                "port": port,
                "data": data,
            }
        # Kui sensor juba olemas, uuenda andmed
        if node in store["entities"]:
            sensor = store["entities"][node]
        else:
            # Loo XSensor heartbeat entity
            sensor = XSensor(hass, type("dummy_entry", (), {"entry_id": node, "options": {}})(), node)
            store["entities"][node] = sensor
            # entity lisamine platformi kaudu
            platform = hass.data.get("sensor", {}).get("platforms", {}).get("sensor")
            if platform:
                hass.async_create_task(platform.async_add_entities([sensor]))

        # Uuenda sensori HA state
        sensor.async_write_ha_state()

        return self.json({"ok": True})