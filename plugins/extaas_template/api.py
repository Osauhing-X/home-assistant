from homeassistant.components.http import HomeAssistantView
from .store import get_store
from .sensor import XSensor
from .const import DOMAIN
import time

class ExtaasAPI(HomeAssistantView):
    """Node -> HA push API."""

    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        node = data.get("node")
        if not node:
            return self.json({"ok": False, "error": "Node name missing"})

        store = get_store(hass)
        store["nodes"].setdefault(node, {})["last_seen"] = time.time()

        # Auto-discovery: salvestame viimase data objekti
        last_data = store["discovered_nodes"].get(node, {}).get("data", {})
        current_keys = set(data.keys()) - {"node", "host", "port"}
        last_keys = set(last_data.keys())

        # Uued võtmed
        new_keys = current_keys - last_keys
        # Kustutatud võtmed
        removed_keys = last_keys - current_keys

        # Salvesta uus data
        store["discovered_nodes"][node] = {
            "host": data.get("host"),
            "port": data.get("port", 3000),
            "data": {k: data[k] for k in current_keys}
        }

        # Init entities dict
        store["entities"].setdefault(node, {})

        # Loo uued sensorid
        for key in new_keys:
            sensor = XSensor(hass, node, key)
            store["entities"][node][key] = {
                "sensor": sensor,
                "value": data[key],
                "last_updated": time.time()
            }
            # Loo entity HA-sse
            platform = hass.data.get("sensor", {}).get("platforms", {}).get("sensor")
            if platform:
                hass.async_create_task(platform.async_add_entities([sensor]))

        # Uuenda olemasolevaid sensorid
        for key in current_keys & last_keys:
            store["entities"][node][key].update({
                "value": data[key],
                "last_updated": time.time()
            })

        # Kustuta sensorid, mis pole enam saadaval
        for key in removed_keys:
            sensor_entry = store["entities"][node].pop(key, None)
            if sensor_entry:
                sensor = sensor_entry["sensor"]
                # HA state removal
                sensor.async_remove()  # eemaldab HA-st

        return self.json({"ok": True})