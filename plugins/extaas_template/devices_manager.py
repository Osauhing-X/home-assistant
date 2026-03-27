import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, SIGNAL_NEW_DATA

_LOGGER = logging.getLogger(__name__)

class ExtaasDevicesManager:
    """Haldab HA entitysid (switchid, sensorid) coordinatori kaudu."""

    def __init__(self, hass, coordinator, entry_id):
        self.hass = hass
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.entities = []

    def setup_entities(self, async_add_entities: AddEntitiesCallback):
        """Loo switchid ja sensorid HA-s."""

        # --- Heartbeat sensor ---
        heartbeat = HeartbeatSensor(self.coordinator)
        async_add_entities([heartbeat])
        self.entities.append(heartbeat)

        # --- Dünaamilised entityd ---
        dynamic_entities = []
        for e in self.coordinator.dynamic_entities:
            if e.get("type") == "switch":
                dynamic_entities.append(DynamicSwitch(self.coordinator, e["name"]))
            else:
                dynamic_entities.append(DynamicSensor(self.coordinator, e["name"]))
        async_add_entities(dynamic_entities)
        self.entities.extend(dynamic_entities)


# --------------------------
# Heartbeat sensor
# --------------------------
class HeartbeatSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._name = f"{coordinator.node_name} Heartbeat"
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.coordinator.heartbeat_state

    async def async_update(self):
        # lihtsalt värskenda coordinatori state
        await self.coordinator.async_refresh_heartbeat()


# --------------------------
# Dünaamiline switch
# --------------------------
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
        self.coordinator.add_to_todo({
            "host": self.coordinator.host,
            "port": self.coordinator.port,
            "name": self._name,
            "value": True
        })

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.async_write_ha_state()
        self.coordinator.add_to_todo({
            "host": self.coordinator.host,
            "port": self.coordinator.port,
            "name": self._name,
            "value": False
        })


# --------------------------
# Dünaamiline sensor
# --------------------------
class DynamicSensor(SensorEntity):
    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        # otsi coordinator.dynamic_entities-st
        for e in self.coordinator.dynamic_entities:
            if e["name"] == self._name:
                return e.get("value", None)
        return None

    async def async_update(self):
        await self.coordinator._async_update_data()