import asyncio, logging, aiohttp
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
HEARTBEAT_INTERVAL = timedelta(seconds=5)

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    return True

async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data.setdefault(DOMAIN, {})

    async def update_entities(node):
        node_name = node.get("node_name")
        host = node.get("host")
        port = node.get("port")
        services = node.get("nodeData", [])

        group_key = f"{node_name}_{host}"
        if group_key not in devices:
            devices[group_key] = {}

        if "heartbeat" not in devices[group_key]:
            hb_sensor = HeartbeatSensor(node_name, host, port, hass)
            devices[group_key]["heartbeat"] = hb_sensor
            async_add_entities([hb_sensor])

        for sensor_info in services:
            sensor_name = sensor_info.get("name")
            key = f"{sensor_name}"
            if key not in devices[group_key]:
                new_sensor = NodeDataSensor(node_name, host, port, sensor_info)
                devices[group_key][key] = new_sensor
                async_add_entities([new_sensor])
            else:
                devices[group_key][key].update(sensor_info)

    hass.data.setdefault(DOMAIN, {})["update_entities"] = update_entities
    return True

class HeartbeatSensor(Entity):
    def __init__(self, node_name, host, port, hass):
        self._node_name = node_name
        self._host = host
        self._port = port
        self._state = False
        self._name = f"{node_name} heartbeat"
        self._unique_id = f"{node_name}_{host}_heartbeat"
        self.hass = hass
        self._cancel = async_track_time_interval(
            hass=hass, action=self._poll, interval=timedelta(seconds=5)
        )

    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._unique_id
    @property
    def state(self): return self._state
    @property
    def icon(self): return "mdi:server-network"
    @property
    def device_class(self): return "connectivity"

    async def _poll(self, now):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/heartbeat", timeout=3) as resp:
                    self._state = resp.status == 200
        except:
            self._state = False
        self.async_write_ha_state()

class NodeDataSensor(Entity):
    def __init__(self, node_name, host, port, sensor_info):
        self._node_name = node_name
        self._host = host
        self._port = port
        self._name = f"{node_name} {sensor_info.get('name')}"
        self._unique_id = f"{node_name}_{host}_{sensor_info.get('name')}"
        self._state = sensor_info.get("value")
        self._icon = sensor_info.get("icon", "mdi:checkbox-blank-outline")
        self._device_class = sensor_info.get("device_class")

    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._unique_id
    @property
    def state(self): return self._state
    @property
    def icon(self): return self._icon
    @property
    def device_class(self): return self._device_class

    def update(self, sensor_info):
        self._state = sensor_info.get("value")
        self._icon = sensor_info.get("icon", "mdi:checkbox-blank-outline")
        self._device_class = sensor_info.get("device_class")
        self.async_write_ha_state()