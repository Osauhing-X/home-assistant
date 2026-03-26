import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
HEARTBEAT_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data.setdefault(DOMAIN, {})

    async def update_entities(data):
        node = data["node_name"]
        host = data["host"]
        port = data["port"]
        service = data["service_name"]
        node_data = data.get("nodeData", [])

        device_key = f"{node}_{service}"

        if device_key not in devices:
            devices[device_key] = {}

        new_entities = []

        # -----------------
        # HEARTBEAT
        # -----------------
        if "heartbeat" not in devices[device_key]:
            hb = HeartbeatSensor(node, service, host, port, hass)
            devices[device_key]["heartbeat"] = hb
            new_entities.append(hb)

        # -----------------
        # NODE DATA
        # -----------------
        for item in node_data:
            name = item.get("name")
            if not name:
                continue

            if name not in devices[device_key]:
                ent = NodeSensor(node, service, item)
                devices[device_key][name] = ent
                new_entities.append(ent)
            else:
                devices[device_key][name].update(item)

        if new_entities:
            async_add_entities(new_entities)

    hass.data[DOMAIN]["update_entities"] = update_entities


# =========================
# HEARTBEAT SENSOR
# =========================
class HeartbeatSensor(Entity):

    def __init__(self, node, service, host, port, hass):
        self._node = node
        self._service = service
        self._host = host
        self._port = port
        self._state = False
        self.hass = hass

        self._attr_name = f"{service} heartbeat"
        self._attr_unique_id = f"{node}_{service}_heartbeat"
        self._attr_icon = "mdi:server"
        self._attr_device_class = "connectivity"

        async_track_time_interval(
            hass, self._poll, HEARTBEAT_INTERVAL
        )

    async def _poll(self, _):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self._host}:{self._port}/heartbeat",
                    timeout=3
                ) as resp:
                    self._state = resp.status == 200
        except:
            self._state = False

        self.async_write_ha_state()

    @property
    def state(self):
        return self._state


# =========================
# NODE SENSOR
# =========================
class NodeSensor(Entity):

    def __init__(self, node, service, data):
        self._node = node
        self._service = service

        self._name = data.get("name")
        self._state = data.get("value")

        self._attr_name = f"{service} {self._name}"
        self._attr_unique_id = f"{node}_{service}_{self._name}"

        self._attr_icon = data.get("icon", "mdi:checkbox-blank-outline")
        self._attr_device_class = data.get("device_class")

    def update(self, data):
        self._state = data.get("value")
        self._attr_icon = data.get("icon", "mdi:checkbox-blank-outline")
        self._attr_device_class = data.get("device_class")
        self.async_write_ha_state()

    @property
    def state(self):
        return self._state