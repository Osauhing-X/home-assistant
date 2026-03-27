import logging
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import SIGNAL_NEW_DATA

_LOGGER = logging.getLogger(__name__)

class ExtaasDevicesManager:
    """Haldab HA entitysid coordinatori kaudu."""

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.entities = []

    def setup_entities(self, async_add_entities: AddEntitiesCallback, entity_type=None):
        """Loo switchid ja sensorid HA-s."""
        entities = []

        if entity_type in (None, "sensor"):
            # Heartbeat sensor
            entities.append(HeartbeatSensor(self.coordinator))

            # Dünaamilised sensorid
            for e in self.coordinator.dynamic_entities:
                if e.get("type") != "switch":
                    entities.append(DynamicSensor(self.coordinator, e["name"]))

        if entity_type in (None, "switch"):
            # Dünaamilised switchid
            for e in self.coordinator.dynamic_entities:
                if e.get("type") == "switch":
                    entities.append(DynamicSwitch(self.coordinator, e["name"]))

        async_add_entities(entities)
        self.entities.extend(entities)


# Heartbeat sensor
class HeartbeatSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._name = f"{coordinator.node_name} Heartbeat"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.coordinator.heartbeat_state

    async def async_update(self):
        await self.coordinator.async_refresh_heartbeat()


# Dünaamiline switch
class DynamicSwitch(SwitchEntity):
    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._name = name
        self._is_on = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.async_write_ha_state()
        self.coordinator.add_to_todo({"host": self.coordinator.host, "port": self.coordinator.port, "name": self._name, "value": True})

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.async_write_ha_state()
        self.coordinator.add_to_todo({"host": self.coordinator.host, "port": self.coordinator.port, "name": self._name, "value": False})


# Dünaamiline sensor
class DynamicSensor(SensorEntity):
    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        for e in self.coordinator.dynamic_entities:
            if e["name"] == self._name:
                return e.get("value")
        return None

    async def async_update(self):
        await self.coordinator._async_update_data()