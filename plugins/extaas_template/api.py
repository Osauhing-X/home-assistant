from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .store import get_store
from .const import DOMAIN, SIGNAL_NEW_DATA
from .sensor import ExtaasSensor
from .switch import ExtaasSwitch

class ExtaasAPI(HomeAssistantView):
    """Node -> HA push API"""
    url = "/api/extaas_template"
    name = "api:extaas_template"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        hostname = data["node_name"]
        service_name = data["service_name"]
        host = data["host"]
        port = data["port"]
        node_data = data["node_data"]

        store = get_store(hass)
        entry_id = hostname

        # --------- ENTRY ---------
        entry = store["entries"].setdefault(entry_id, {"name": hostname, "devices": {}})

        # --------- DEVICE ---------
        device_id = f"{host}:{port}"
        device = entry["devices"].setdefault(device_id, {
            "name": service_name,
            "host": host,
            "port": port,
            "icon": None,
            "entities": {}
        })

        # --------- ENTITIES ---------
        for item in node_data:
            unique_id = f"{entry_id}:{device_id}:{item['name']}"
            if unique_id not in store["entities"]:
                entity_data = {**item, "unique_id": unique_id}
                if item["type"] == "switch":
                    entity = ExtaasSwitch(hass, entry_id, device, entity_data)
                else:
                    entity = ExtaasSensor(hass, entry_id, device, entity_data)
                device["entities"][unique_id] = entity
                store["entities"][unique_id] = entity

                # Add entity to HA
                platform = hass.data.get(item["type"], {}).get("platforms", {}).get(item["type"])
                if platform:
                    hass.async_create_task(platform.async_add_entities([entity]))
            else:
                # Update existing entity
                entity = store["entities"][unique_id]
                entity._attr_state = item["value"]

        async_dispatcher_send(hass, SIGNAL_NEW_DATA)
        return self.json({"ok": True})