import logging
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "extaas_template"
_ENTITIES = {}  # entity_id -> ExTaaS_Sensor

def update_entities(service_payload):
    """
    Uuenda teenuse sensorid.
    Payload peab olema kujul:
    {
        "node": "taavi-book-13",
        "service": "Website",
        "host": "10.1.1.74",
        "port": 3010,
        "data": [{ 
           "name": "web",
           "value": true,
           "icon": "mdi:connection",
           "device_class": "connectivity" },
           ... ]}
    """
    node_name = service_payload.get("node")
    service_name = service_payload.get("service")
    host = service_payload.get("host")
    port = service_payload.get("port")
    data_list = service_payload.get("data", [])

    if not node_name or not service_name:
        _LOGGER.warning("Payloadil puudub node või service nimi")
        return

    for item in data_list:
        name = item.get("name")
        if not name:
            continue

        value = item.get("value")
        icon = item.get("icon", "mdi:checkbox-blank-outline")
        device_class = item.get("device_class")

        entity_id = f"{node_name}_{service_name}_{name}".lower().replace(" ", "_")
        if entity_id not in _ENTITIES:
            _ENTITIES[entity_id] = ExTaaS_Sensor(
                node_name=node_name,
                service_name=service_name,
                sensor_name=name,
                value=value,
                icon=icon,
                device_class=device_class,
                host=host,
                port=port
            )
        else:
            _ENTITIES[entity_id].update_data(value, icon, device_class, host, port)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Lisab kõik olemasolevad sensorid HA-sse."""
    async_add_entities(_ENTITIES.values())


class ExTaaS_Sensor(Entity):
    def __init__(self, node_name, service_name, sensor_name, value, icon, device_class, host=None, port=None):
        self.node_name = node_name
        self.service_name = service_name
        self.sensor_name = sensor_name
        self._value = value
        self._icon = icon
        self._device_class = device_class
        self.host = host
        self.port = port

        self._attr_name = f"{node_name} ← {service_name}"
        self._attr_unique_id = f"{node_name}_{service_name}_{sensor_name}".lower().replace(" ", "_")

    @property
    def state(self):
        return self._value

    @property
    def icon(self):
        return self._icon or "mdi:checkbox-blank-outline"

    @property
    def device_class(self):
        return self._device_class

    @property
    def extra_state_attributes(self):
        return {
            "host": self.host,
            "port": self.port,
            "sensor_name": self.sensor_name
        }

    def update(self):
        """HA kutsub update, sensoril pole midagi lisaks teha"""
        pass

    def update_data(self, value, icon=None, device_class=None, host=None, port=None):
        self._value = value
        self._icon = icon or "mdi:checkbox-blank-outline"
        self._device_class = device_class
        self.host = host
        self.port = port