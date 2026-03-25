# sensor.py
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

class ExTaaSSensor(Entity):
    def __init__(self, node_name, host, port, service_name, name, value, icon=None, device_class=None):
        self._node_name = node_name
        self._host = host
        self._port = port
        self._service_name = service_name
        self._name = name
        self._state = value
        self._icon = icon or "mdi:checkbox-blank-outline"
        self._device_class = device_class

    @property
    def name(self):
        # Kuvab: Node ← Teenus (IP:Port)
        return f"{self._node_name} ← {self._service_name} ({self._host}:{self._port})"

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        return self._device_class

    @property
    def extra_state_attributes(self):
        return {
            "host": self._host,
            "port": self._port,
            "sensor_name": self._name
        }

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors from config entry / discovery_info."""
    node = entry.data  # peaks sisaldama: node_name, host, port, service_name, node_data
    node_name = node.get("node_name")
    host = node.get("host")
    port = node.get("port")
    service_name = node.get("service_name")
    node_data = node.get("node_data", [])

    sensors = []
    for item in node_data:
        sensors.append(
            ExTaaSSensor(
                node_name=node_name,
                host=host,
                port=port,
                service_name=service_name,
                name=item["name"],
                value=item["value"],
                icon=item.get("icon"),
                device_class=item.get("device_class"),
            )
        )

    async_add_entities(sensors, update_before_add=True)