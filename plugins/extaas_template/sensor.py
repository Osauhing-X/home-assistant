import aiohttp
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.device_registry import async_get as get_device_registry
from .const import DOMAIN

SCAN = timedelta(seconds=5)

async def async_setup_entry(hass, entry, async_add_entities):
    store = {}
    device_registry = get_device_registry(hass)

    async def update_entities(data):
        host = data["host"]
        port = data["port"]
        service = data["service_name"]
        node_name = data["node_name"]
        node_data = data.get("node_data", [])

        if host != entry.data["host"]:
            return

        parent = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, host)},
            name=entry.data["name"],
            manufacturer="Extaas",
            model="Node"
        )

        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"{host}:{port}")},
            name=service,
            manufacturer="Extaas",
            model="Service",
            via_device=(DOMAIN, host)
        )

        key = f"{host}:{port}"

        if key not in store:
            store[key] = {}
            hb = HeartbeatSensor(hass, host, port, service, device.id)
            store[key]["heartbeat"] = hb
            async_add_entities([hb])

        existing = set(store[key].keys())

        for item in node_data:
            name = item["name"]
            if name not in store[key]:
                ent = NodeSensor(item, service, device.id)
                store[key][name] = ent
                async_add_entities([ent])
            else:
                store[key][name].update(item)

        new_keys = {i["name"] for i in node_data}
        for old in list(existing):
            if old not in new_keys and old != "heartbeat":
                ent = store[key].pop(old)
                await ent.async_remove()

    hass.data.setdefault(DOMAIN, {})["update_entities"] = update_entities

class HeartbeatSensor(Entity):
    def __init__(self, hass, host, port, service, device_id):
        self._state = False
        self._host = host
        self._port = port

        self._attr_name = f"{service} heartbeat"
        self._attr_unique_id = f"{host}_{port}_heartbeat"
        self._attr_device_info = {"identifiers": {(DOMAIN, device_id)}}

        async_track_time_interval(hass, self._poll, SCAN)

    async def _poll(self, now):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"http://{self._host}:{self._port}/heartbeat", timeout=3) as r:
                    self._state = r.status == 200
        except:
            self._state = False
        self.async_write_ha_state()

    @property
    def state(self): return self._state
    @property
    def icon(self): return "mdi:server"
    @property
    def device_class(self): return "connectivity"

class NodeSensor(Entity):
    def __init__(self, data, service, device_id):
        self._attr_name = f"{service} {data['name']}"
        self._attr_unique_id = f"{service}_{data['name']}"
        self._attr_device_info = {"identifiers": {(DOMAIN, device_id)}}
        self.update(data)

    def update(self, data):
        self._state = data["value"]
        self._icon = data.get("icon", "mdi:checkbox-blank-outline")
        self._device_class = data.get("device_class")
        self.async_write_ha_state()

    @property
    def state(self): return self._state
    @property
    def icon(self): return self._icon
    @property
    def device_class(self): return self._device_class